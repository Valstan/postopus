"""
VK API integration endpoints for Postopus
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

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

router = APIRouter(prefix="/api/vk", tags=["vk"])


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
        with db.get_session() as session:
            tokens = session.query(VKToken).all()
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
        with db.get_session() as session:
            # Проверяем, что токен для региона не существует
            existing = session.query(VKToken).filter(VKToken.region == token_data.region).first()
            if existing:
                raise HTTPException(status_code=400, detail=f"Token for region {token_data.region} already exists")
            
            token = VKToken(
                region=token_data.region,
                token=token_data.token,
                group_id=token_data.group_id,
                description=token_data.description,
                is_active=True
            )
            session.add(token)
            session.commit()
            session.refresh(token)
            
            return {
                "message": "VK token created successfully",
                "token": {
                    "id": token.id,
                    "region": token.region,
                    "group_id": token.group_id,
                    "description": token.description,
                    "is_active": token.is_active
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating VK token: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/tokens/{token_id}")
async def update_vk_token(token_id: int, token_data: VKTokenUpdate):
    """Обновить VK токен."""
    try:
        db = get_database()
        with db.get_session() as session:
            token = session.query(VKToken).filter(VKToken.id == token_id).first()
            if not token:
                raise HTTPException(status_code=404, detail="Token not found")
            
            if token_data.token is not None:
                token.token = token_data.token
            if token_data.group_id is not None:
                token.group_id = token_data.group_id
            if token_data.description is not None:
                token.description = token_data.description
            if token_data.is_active is not None:
                token.is_active = token_data.is_active
            
            token.updated_at = datetime.utcnow()
            session.commit()
            
            return {
                "message": "VK token updated successfully",
                "token": {
                    "id": token.id,
                    "region": token.region,
                    "group_id": token.group_id,
                    "description": token.description,
                    "is_active": token.is_active
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating VK token: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/tokens/{token_id}")
async def delete_vk_token(token_id: int):
    """Удалить VK токен."""
    try:
        db = get_database()
        with db.get_session() as session:
            token = session.query(VKToken).filter(VKToken.id == token_id).first()
            if not token:
                raise HTTPException(status_code=404, detail="Token not found")
            
            session.delete(token)
            session.commit()
            
            return {"message": "VK token deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting VK token: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# VK Connection Testing
@router.get("/test-connections")
async def test_vk_connections():
    """Тестировать подключения к VK API."""
    try:
        vk_service = ModernVKService()
        
        # Инициализируем сервис
        initialized = await vk_service.initialize()
        if not initialized:
            raise HTTPException(status_code=500, detail="Failed to initialize VK service")
        
        # Тестируем подключения
        results = await vk_service.test_connection()
        
        return {
            "message": f"Tested {results['total_tokens']} tokens, {results['working_tokens']} working",
            "results": results
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing VK connections: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# VK Post Management
@router.post("/fetch-posts")
async def fetch_posts_from_region(request: VKRegionSyncRequest, background_tasks: BackgroundTasks):
    """Получить посты из VK групп региона."""
    try:
        # Запускаем задачу в фоне
        task = fetch_posts_from_region_task.delay(request.region, request.count)
        
        return {
            "message": f"Started fetching posts from region {request.region}",
            "task_id": task.id,
            "region": request.region,
            "count": request.count
        }
    except Exception as e:
        logger.error(f"Error fetching posts from region: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/publish-post")
async def publish_post_to_vk(request: VKPostRequest, background_tasks: BackgroundTasks):
    """Опубликовать пост в VK группы."""
    try:
        # Проверяем, что пост существует
        db = get_database()
        with db.get_session() as session:
            post = session.query(Post).filter(Post.id == request.post_id).first()
            if not post:
                raise HTTPException(status_code=404, detail="Post not found")
        
        # Запускаем задачу в фоне
        task = publish_post_to_vk_task.delay(
            request.post_id,
            request.target_groups,
            request.region
        )
        
        return {
            "message": f"Started publishing post {request.post_id}",
            "task_id": task.id,
            "post_id": request.post_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error publishing post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-all-regions")
async def sync_all_regions(background_tasks: BackgroundTasks):
    """Синхронизировать посты из всех регионов."""
    try:
        # Запускаем задачу в фоне
        task = sync_all_regions_task.delay()
        
        return {
            "message": "Started syncing all regions",
            "task_id": task.id
        }
    except Exception as e:
        logger.error(f"Error syncing all regions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process-scheduled-posts")
async def process_scheduled_posts(background_tasks: BackgroundTasks):
    """Обработать запланированные посты."""
    try:
        # Запускаем задачу в фоне
        task = process_scheduled_posts_task.delay()
        
        return {
            "message": "Started processing scheduled posts",
            "task_id": task.id
        }
    except Exception as e:
        logger.error(f"Error processing scheduled posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# VK Group Management
@router.get("/groups")
async def get_vk_groups():
    """Получить список VK групп."""
    try:
        db = get_database()
        with db.get_session() as session:
            groups = session.query(Group).filter(Group.platform == 'vk').all()
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
        
        # Инициализируем сервис
        initialized = await vk_service.initialize()
        if not initialized:
            raise HTTPException(status_code=500, detail="Failed to initialize VK service")
        
        # Получаем информацию о группе
        group_info = await vk_service.get_group_info(group_id)
        
        if not group_info:
            raise HTTPException(status_code=404, detail="Group not found")
        
        return {
            "message": "Group info retrieved successfully",
            "group_info": group_info
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting group info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# VK Statistics
@router.get("/statistics")
async def get_vk_statistics():
    """Получить статистику VK интеграции."""
    try:
        db = get_database()
        with db.get_session() as session:
            # Статистика токенов
            total_tokens = session.query(VKToken).count()
            active_tokens = session.query(VKToken).filter(VKToken.is_active == True).count()
            
            # Статистика групп
            total_groups = session.query(Group).filter(Group.platform == 'vk').count()
            active_groups = session.query(Group).filter(
                Group.platform == 'vk',
                Group.is_active == True
            ).count()
            
            # Статистика постов
            total_posts = session.query(Post).count()
            published_posts = session.query(Post).filter(Post.status == 'published').count()
            pending_posts = session.query(Post).filter(Post.status == 'pending').count()
            
            return {
                "tokens": {
                    "total": total_tokens,
                    "active": active_tokens,
                    "inactive": total_tokens - active_tokens
                },
                "groups": {
                    "total": total_groups,
                    "active": active_groups,
                    "inactive": total_groups - active_groups
                },
                "posts": {
                    "total": total_posts,
                    "published": published_posts,
                    "pending": pending_posts
                }
            }
    except Exception as e:
        logger.error(f"Error getting VK statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Task Status
@router.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """Получить статус задачи."""
    try:
        from ..tasks.celery_app import celery_app
        
        result = celery_app.AsyncResult(task_id)
        
        return {
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready() else None,
            "info": result.info if not result.successful() else None
        }
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
