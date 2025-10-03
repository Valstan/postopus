#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VK API Router для Postopus
Исправленная версия с правильной работой с базой данных
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel

from ..database import get_database
from ..models import Post, Group, VKToken
from ...services.modern_vk_service import ModernVKService
from ...tasks.vk_tasks import (
    fetch_posts_from_region_task,
    publish_post_to_vk_task,
    test_vk_connections_task,
    process_scheduled_posts_task,
    update_post_statistics_task,
    sync_all_regions_task
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models
class VKTokenCreate(BaseModel):
    region: str
    token: str
    group_id: str
    description: Optional[str] = None

class VKTokenUpdate(BaseModel):
    token: Optional[str] = None
    group_id: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class VKPostRequest(BaseModel):
    post_id: int
    target_groups: Optional[List[str]] = None
    region: Optional[str] = None

class VKRegionSyncRequest(BaseModel):
    region: str
    count: int = 20

# VK Token Management
@router.get("/tokens")
async def get_vk_tokens():
    """Получить список VK токенов."""
    try:
        db = get_database()
        tokens = db.query(VKToken).all()
        return {
            "tokens": [
                {
                    "id": token.id,
                    "region": token.region,
                    "group_id": token.group_id,
                    "description": token.description,
                    "is_active": token.is_active,
                    "created_at": token.created_at.isoformat(),
                    "last_used": token.last_used.isoformat() if token.last_used else None
                }
                for token in tokens
            ],
            "total": len(tokens)
        }
    except Exception as e:
        logger.error(f"Error getting VK tokens: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tokens")
async def create_vk_token(token_data: VKTokenCreate):
    """Создать новый VK токен."""
    try:
        db = get_database()
        
        # Проверяем, существует ли уже токен для этого региона
        existing_token = db.query(VKToken).filter(VKToken.region == token_data.region).first()
        if existing_token:
            raise HTTPException(status_code=400, detail=f"Token for region {token_data.region} already exists")
        
        # Создаем новый токен
        new_token = VKToken(
            region=token_data.region,
            token=token_data.token,
            group_id=token_data.group_id,
            description=token_data.description,
            is_active=True
        )
        
        db.add(new_token)
        db.commit()
        db.refresh(new_token)
        
        return {
            "id": new_token.id,
            "region": new_token.region,
            "group_id": new_token.group_id,
            "description": new_token.description,
            "is_active": new_token.is_active,
            "created_at": new_token.created_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating VK token: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/tokens/{token_id}")
async def update_vk_token(token_id: int, token_data: VKTokenUpdate):
    """Обновить VK токен."""
    try:
        db = get_database()
        token = db.query(VKToken).filter(VKToken.id == token_id).first()
        
        if not token:
            raise HTTPException(status_code=404, detail="Token not found")
        
        # Обновляем поля
        if token_data.token is not None:
            token.token = token_data.token
        if token_data.group_id is not None:
            token.group_id = token_data.group_id
        if token_data.description is not None:
            token.description = token_data.description
        if token_data.is_active is not None:
            token.is_active = token_data.is_active
        
        db.commit()
        db.refresh(token)
        
        return {
            "id": token.id,
            "region": token.region,
            "group_id": token.group_id,
            "description": token.description,
            "is_active": token.is_active,
            "updated_at": token.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating VK token: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/tokens/{token_id}")
async def delete_vk_token(token_id: int):
    """Удалить VK токен."""
    try:
        db = get_database()
        token = db.query(VKToken).filter(VKToken.id == token_id).first()
        
        if not token:
            raise HTTPException(status_code=404, detail="Token not found")
        
        db.delete(token)
        db.commit()
        
        return {"message": "Token deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting VK token: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# VK API Operations
@router.get("/test-connections")
async def test_vk_connections():
    """Тестировать подключения к VK API."""
    try:
        vk_service = ModernVKService()
        success = await vk_service.initialize()
        
        if success:
            return {
                "status": "success",
                "message": f"VK service initialized with {len(vk_service.tokens)} tokens",
                "tokens": list(vk_service.tokens.keys())
            }
        else:
            return {
                "status": "failed",
                "message": "Failed to initialize VK service",
                "tokens": []
            }
    except Exception as e:
        logger.error(f"Error testing VK connections: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fetch-posts")
async def fetch_posts_from_region(request: VKRegionSyncRequest, background_tasks: BackgroundTasks):
    """Получить посты из VK групп региона."""
    try:
        # Запускаем задачу в фоне
        task = fetch_posts_from_region_task.delay(request.region, request.count)
        
        return {
            "status": "started",
            "task_id": task.id,
            "message": f"Fetching posts from region {request.region}",
            "count": request.count
        }
    except Exception as e:
        logger.error(f"Error starting fetch posts task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/publish-post")
async def publish_post_to_vk(request: VKPostRequest, background_tasks: BackgroundTasks):
    """Опубликовать пост в VK группы."""
    try:
        # Запускаем задачу в фоне
        task = publish_post_to_vk_task.delay(request.post_id, request.target_groups, request.region)
        
        return {
            "status": "started",
            "task_id": task.id,
            "message": f"Publishing post {request.post_id} to VK",
            "target_groups": request.target_groups,
            "region": request.region
        }
    except Exception as e:
        logger.error(f"Error starting publish post task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync-all-regions")
async def sync_all_regions(background_tasks: BackgroundTasks):
    """Синхронизировать посты из всех регионов."""
    try:
        # Запускаем задачу в фоне
        task = sync_all_regions_task.delay()
        
        return {
            "status": "started",
            "task_id": task.id,
            "message": "Syncing posts from all regions"
        }
    except Exception as e:
        logger.error(f"Error starting sync all regions task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-scheduled-posts")
async def process_scheduled_posts(background_tasks: BackgroundTasks):
    """Обработать запланированные посты."""
    try:
        # Запускаем задачу в фоне
        task = process_scheduled_posts_task.delay()
        
        return {
            "status": "started",
            "task_id": task.id,
            "message": "Processing scheduled posts"
        }
    except Exception as e:
        logger.error(f"Error starting process scheduled posts task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/groups")
async def get_vk_groups():
    """Получить список VK групп."""
    try:
        db = get_database()
        groups = db.query(Group).filter(Group.platform == "vk").all()
        
        return {
            "groups": [
                {
                    "id": group.id,
                    "name": group.name,
                    "group_id": group.group_id,
                    "region": group.region,
                    "is_active": group.is_active,
                    "created_at": group.created_at.isoformat()
                }
                for group in groups
            ],
            "total": len(groups)
        }
    except Exception as e:
        logger.error(f"Error getting VK groups: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/groups/{group_id}/info")
async def get_vk_group_info(group_id: str):
    """Получить информацию о VK группе."""
    try:
        vk_service = ModernVKService()
        await vk_service.initialize()
        
        # Получаем информацию о группе через VK API
        group_info = await vk_service.get_group_info(group_id)
        
        return {
            "group_id": group_id,
            "info": group_info
        }
    except Exception as e:
        logger.error(f"Error getting VK group info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_vk_statistics():
    """Получить статистику VK интеграции."""
    try:
        db = get_database()
        
        # Статистика токенов
        total_tokens = db.query(VKToken).count()
        active_tokens = db.query(VKToken).filter(VKToken.is_active == True).count()
        
        # Статистика групп
        total_groups = db.query(Group).filter(Group.platform == "vk").count()
        active_groups = db.query(Group).filter(Group.platform == "vk", Group.is_active == True).count()
        
        # Статистика постов
        total_posts = db.query(Post).count()
        published_posts = db.query(Post).filter(Post.status == "published").count()
        
        return {
            "tokens": {
                "total": total_tokens,
                "active": active_tokens
            },
            "groups": {
                "total": total_groups,
                "active": active_groups
            },
            "posts": {
                "total": total_posts,
                "published": published_posts
            }
        }
    except Exception as e:
        logger.error(f"Error getting VK statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """Получить статус задачи."""
    try:
        # Здесь можно добавить логику для получения статуса Celery задачи
        return {
            "task_id": task_id,
            "status": "unknown",
            "message": "Task status tracking not implemented yet"
        }
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
