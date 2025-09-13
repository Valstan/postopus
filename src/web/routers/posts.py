"""
Роутер для управления постами.
"""
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ..database import get_database
from ..auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

class PostCreate(BaseModel):
    """Модель для создания поста."""
    text: str
    attachments: Optional[List[str]] = None
    scheduled_at: Optional[datetime] = None
    target_platforms: List[str] = ["vk"]

class PostUpdate(BaseModel):
    """Модель для обновления поста."""
    text: Optional[str] = None
    attachments: Optional[List[str]] = None
    scheduled_at: Optional[datetime] = None
    target_platforms: Optional[List[str]] = None

class PostResponse(BaseModel):
    """Модель для ответа с постом."""
    id: str
    text: str
    attachments: List[str]
    status: str
    published_at: Optional[datetime]
    scheduled_at: Optional[datetime]
    target_platforms: List[str]
    views: int
    likes: int
    reposts: int
    created_at: datetime
    updated_at: datetime

@router.get("/", response_model=List[PostResponse])
async def get_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    platform: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Получает список постов."""
    try:
        posts_collection = db.get_collection("posts")
        
        # Строим фильтр
        filter_dict = {}
        if status:
            filter_dict["status"] = status
        if platform:
            filter_dict["target_platforms"] = {"$in": [platform]}
        
        # Получаем посты
        posts = await posts_collection.find(
            filter_dict,
            {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
        
        return [
            PostResponse(
                id=post["id"],
                text=post["text"],
                attachments=post.get("attachments", []),
                status=post["status"],
                published_at=post.get("published_at"),
                scheduled_at=post.get("scheduled_at"),
                target_platforms=post.get("target_platforms", []),
                views=post.get("views", 0),
                likes=post.get("likes", 0),
                reposts=post.get("reposts", 0),
                created_at=post["created_at"],
                updated_at=post["updated_at"]
            )
            for post in posts
        ]
        
    except Exception as e:
        logger.error(f"Error getting posts: {e}")
        raise HTTPException(status_code=500, detail="Error getting posts")

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Получает пост по ID."""
    try:
        posts_collection = db.get_collection("posts")
        post = await posts_collection.find_one({"id": post_id}, {"_id": 0})
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        return PostResponse(
            id=post["id"],
            text=post["text"],
            attachments=post.get("attachments", []),
            status=post["status"],
            published_at=post.get("published_at"),
            scheduled_at=post.get("scheduled_at"),
            target_platforms=post.get("target_platforms", []),
            views=post.get("views", 0),
            likes=post.get("likes", 0),
            reposts=post.get("reposts", 0),
            created_at=post["created_at"],
            updated_at=post["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting post {post_id}: {e}")
        raise HTTPException(status_code=500, detail="Error getting post")

@router.post("/", response_model=PostResponse)
async def create_post(
    post_data: PostCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Создает новый пост."""
    try:
        posts_collection = db.get_collection("posts")
        
        # Генерируем ID поста
        post_id = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(post_data.text) % 10000}"
        
        # Создаем пост
        post = {
            "id": post_id,
            "text": post_data.text,
            "attachments": post_data.attachments or [],
            "status": "draft" if post_data.scheduled_at else "ready",
            "published_at": None,
            "scheduled_at": post_data.scheduled_at,
            "target_platforms": post_data.target_platforms,
            "views": 0,
            "likes": 0,
            "reposts": 0,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Сохраняем в базу данных
        await posts_collection.insert_one(post)
        
        # Если пост не запланирован, добавляем в очередь на публикацию
        if not post_data.scheduled_at:
            # Здесь должна быть логика добавления в очередь Celery
            pass
        
        return PostResponse(**post)
        
    except Exception as e:
        logger.error(f"Error creating post: {e}")
        raise HTTPException(status_code=500, detail="Error creating post")

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: str,
    post_data: PostUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Обновляет пост."""
    try:
        posts_collection = db.get_collection("posts")
        
        # Проверяем, существует ли пост
        existing_post = await posts_collection.find_one({"id": post_id}, {"_id": 0})
        if not existing_post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Обновляем только переданные поля
        update_data = {"updated_at": datetime.now()}
        if post_data.text is not None:
            update_data["text"] = post_data.text
        if post_data.attachments is not None:
            update_data["attachments"] = post_data.attachments
        if post_data.scheduled_at is not None:
            update_data["scheduled_at"] = post_data.scheduled_at
        if post_data.target_platforms is not None:
            update_data["target_platforms"] = post_data.target_platforms
        
        # Обновляем статус
        if post_data.scheduled_at:
            update_data["status"] = "scheduled"
        elif existing_post["status"] == "draft":
            update_data["status"] = "ready"
        
        # Сохраняем изменения
        await posts_collection.update_one(
            {"id": post_id},
            {"$set": update_data}
        )
        
        # Получаем обновленный пост
        updated_post = await posts_collection.find_one({"id": post_id}, {"_id": 0})
        
        return PostResponse(**updated_post)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating post {post_id}: {e}")
        raise HTTPException(status_code=500, detail="Error updating post")

@router.delete("/{post_id}")
async def delete_post(
    post_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Удаляет пост."""
    try:
        posts_collection = db.get_collection("posts")
        
        # Проверяем, существует ли пост
        existing_post = await posts_collection.find_one({"id": post_id}, {"_id": 0})
        if not existing_post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Удаляем пост
        await posts_collection.delete_one({"id": post_id})
        
        return {"message": "Post deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting post {post_id}: {e}")
        raise HTTPException(status_code=500, detail="Error deleting post")

@router.post("/{post_id}/publish")
async def publish_post(
    post_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Публикует пост немедленно."""
    try:
        posts_collection = db.get_collection("posts")
        
        # Проверяем, существует ли пост
        existing_post = await posts_collection.find_one({"id": post_id}, {"_id": 0})
        if not existing_post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Обновляем статус
        await posts_collection.update_one(
            {"id": post_id},
            {
                "$set": {
                    "status": "publishing",
                    "updated_at": datetime.now()
                }
            }
        )
        
        # Здесь должна быть логика публикации через Celery
        # publish_post_task.delay(post_id)
        
        return {"message": "Post queued for publishing"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error publishing post {post_id}: {e}")
        raise HTTPException(status_code=500, detail="Error publishing post")
