"""
Enhanced posts router with PostgreSQL integration and regional support.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from pydantic import BaseModel

try:
    from sqlalchemy.orm import Session
    from sqlalchemy import select, and_, or_, func
    from ...database.postgres import async_session, Post
except ImportError:
    Session = None
    async_session = None
    Post = None

from ...services.vk_service import EnhancedVKService
from ...services.post_processor import EnhancedPostProcessor
from ...models.config import AppConfig
from .auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# Enhanced Pydantic models
class PostCreate(BaseModel):
    """Enhanced model for creating posts."""
    title: str
    content: str
    region: str
    theme: str = "novost"
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    vk_group_id: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    tags: List[str] = []
    priority: int = 0  # 0=normal, 1=high, -1=low

class PostUpdate(BaseModel):
    """Enhanced model for updating posts."""
    title: Optional[str] = None
    content: Optional[str] = None
    region: Optional[str] = None
    theme: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    vk_group_id: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    tags: Optional[List[str]] = None
    priority: Optional[int] = None

class PostResponse(BaseModel):
    """Enhanced model for post responses."""
    id: int
    title: str
    content: str
    region: str
    theme: str
    image_url: Optional[str]
    video_url: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    scheduled_at: Optional[datetime]
    published_at: Optional[datetime] = None
    vk_group_id: Optional[str]
    telegram_chat_id: Optional[str]
    tags: List[str]
    view_count: int = 0
    like_count: int = 0
    priority: int
    source_url: Optional[str] = None
    post_metadata: Dict[str, Any] = {}

class PostStats(BaseModel):
    """Post statistics model."""
    total_posts: int
    published_posts: int
    scheduled_posts: int
    draft_posts: int
    by_region: Dict[str, int]
    by_theme: Dict[str, int]
    by_status: Dict[str, int]

class PublishRequest(BaseModel):
    """Request model for publishing posts."""
    target_groups: List[str] = []
    delay_minutes: int = 0
    add_hashtags: bool = True

@router.get("/", response_model=List[PostResponse])
async def get_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    region: Optional[str] = Query(None),
    theme: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Get list of posts with advanced filtering."""
    try:
        if not async_session or not Post:
            # Fallback to demo data
            return [
                PostResponse(
                    id=1,
                    title="Demo: Новости Малмыжа",
                    content="Демонстрационный пост с новостями региона",
                    region="mi",
                    theme="novost",
                    status="published",
                    image_url=None,
                    video_url=None,
                    scheduled_at=None,
                    vk_group_id="mi_group",
                    telegram_chat_id=None,
                    tags=["демо", "новости"],
                    priority=0,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ),
                PostResponse(
                    id=2,
                    title="Demo: Развлечения Нолинска",
                    content="Развлекательный контент для региона",
                    region="nolinsk",
                    theme="prikol",
                    status="draft",
                    image_url="https://example.com/image.jpg",
                    video_url=None,
                    scheduled_at=datetime.now() + timedelta(hours=2),
                    vk_group_id="nolinsk_group",
                    telegram_chat_id="@nolinsk_chat",
                    tags=["демо", "развлечения"],
                    priority=1,
                    created_at=datetime.now() - timedelta(hours=1),
                    updated_at=datetime.now()
                )
            ]
        
        query = select(Post)
        
        # Apply filters
        if region:
            query = query.where(Post.region == region)
        if theme:
            query = query.where(Post.theme == theme)
        if status:
            query = query.where(Post.status == status)
            
        # Apply pagination and ordering
        query = query.offset(skip).limit(limit).order_by(Post.created_at.desc())
        
        async with async_session() as session:
            result = await session.execute(query)
            posts = result.scalars().all()
            
            # Convert to response format
            return [
                PostResponse(
                    id=post.id,
                    title=post.title,
                    content=post.content,
                    region=post.region,
                    theme=post.theme,
                    status=post.status,
                    image_url=post.image_url,
                    video_url=post.video_url,
                    scheduled_at=post.scheduled_at,
                    vk_group_id=post.vk_group_id,
                    telegram_chat_id=post.telegram_chat_id,
                    tags=post.tags or [],
                    priority=post.priority,
                    created_at=post.created_at,
                    updated_at=post.updated_at
                ) for post in posts
            ]
    except Exception as e:
        logger.error(f"Error fetching posts: {e}")
        # Return demo data on error
        return []

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get a single post by ID."""
    try:
        if not async_session or not Post:
            raise HTTPException(status_code=500, detail="Database not available")
        
        async with async_session() as session:
            query = select(Post).where(Post.id == post_id)
            result = await session.execute(query)
            post = result.scalar_one_or_none()
            
            if not post:
                raise HTTPException(status_code=404, detail="Post not found")
            
            return PostResponse(
                id=post.id,
                title=post.title,
                content=post.content,
                region=post.region,
                theme=post.theme,
                status=post.status,
                image_url=post.image_url,
                video_url=post.video_url,
                scheduled_at=post.scheduled_at,
                vk_group_id=post.vk_group_id,
                telegram_chat_id=post.telegram_chat_id,
                tags=post.tags or [],
                priority=post.priority,
                created_at=post.created_at,
                updated_at=post.updated_at
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching post {post_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching post: {str(e)}")

@router.post("/", response_model=PostResponse)
async def create_post(
    post_data: PostCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new post with enhanced features."""
    try:
        # Validate region
        valid_regions = [
            'mi', 'nolinsk', 'arbazh', 'kirs', 'slob', 'verhosh', 'bogord',
            'yaransk', 'viatpol', 'zuna', 'darov', 'kilmez', 'lebazh', 'omut', 'san'
        ]
        if post_data.region not in valid_regions:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid region. Must be one of: {', '.join(valid_regions)}"
            )
        
        # Validate theme
        valid_themes = ['novost', 'sosed', 'kino', 'music', 'prikol', 'reklama']
        if post_data.theme not in valid_themes:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid theme. Must be one of: {', '.join(valid_themes)}"
            )
        
        if not async_session or not Post:
            raise HTTPException(status_code=500, detail="Database not available")
        
        new_post = Post(
            title=post_data.title,
            content=post_data.content,
            region=post_data.region,
            theme=post_data.theme,
            status="draft",  # Always start as draft
            image_url=post_data.image_url,
            video_url=post_data.video_url,
            scheduled_at=post_data.scheduled_at,
            vk_group_id=post_data.vk_group_id,
            telegram_chat_id=post_data.telegram_chat_id,
            tags=post_data.tags,
            priority=post_data.priority,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        async with async_session() as session:
            session.add(new_post)
            await session.commit()
            await session.refresh(new_post)
            
            # Return enhanced response
            return PostResponse(
                id=new_post.id,
                title=new_post.title,
                content=new_post.content,
                region=new_post.region,
                theme=new_post.theme,
                status=new_post.status,
                image_url=new_post.image_url,
                video_url=new_post.video_url,
                scheduled_at=new_post.scheduled_at,
                vk_group_id=new_post.vk_group_id,
                telegram_chat_id=new_post.telegram_chat_id,
                tags=new_post.tags or [],
                priority=new_post.priority,
                created_at=new_post.created_at,
                updated_at=new_post.updated_at
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating post: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create post: {str(e)}")

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an existing post."""
    try:
        if not async_session or not Post:
            raise HTTPException(status_code=500, detail="Database not available")
        
        async with async_session() as session:
            # Get existing post
            query = select(Post).where(Post.id == post_id)
            result = await session.execute(query)
            existing_post = result.scalar_one_or_none()
            
            if not existing_post:
                raise HTTPException(status_code=404, detail="Post not found")
            
            # Update fields
            update_data = {}
            if post_data.title is not None:
                update_data["title"] = post_data.title
            if post_data.content is not None:
                update_data["content"] = post_data.content
            if post_data.region is not None:
                # Validate region
                valid_regions = [
                    'mi', 'nolinsk', 'arbazh', 'kirs', 'slob', 'verhosh', 'bogord',
                    'yaransk', 'viatpol', 'zuna', 'darov', 'kilmez', 'lebazh', 'omut', 'san'
                ]
                if post_data.region not in valid_regions:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Invalid region. Must be one of: {', '.join(valid_regions)}"
                    )
                update_data["region"] = post_data.region
            if post_data.theme is not None:
                # Validate theme
                valid_themes = ['novost', 'sosed', 'kino', 'music', 'prikol', 'reklama']
                if post_data.theme not in valid_themes:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Invalid theme. Must be one of: {', '.join(valid_themes)}"
                    )
                update_data["theme"] = post_data.theme
            if post_data.image_url is not None:
                update_data["image_url"] = post_data.image_url
            if post_data.video_url is not None:
                update_data["video_url"] = post_data.video_url
            if post_data.scheduled_at is not None:
                update_data["scheduled_at"] = post_data.scheduled_at
            if post_data.vk_group_id is not None:
                update_data["vk_group_id"] = post_data.vk_group_id
            if post_data.telegram_chat_id is not None:
                update_data["telegram_chat_id"] = post_data.telegram_chat_id
            if post_data.tags is not None:
                update_data["tags"] = post_data.tags
            if post_data.priority is not None:
                update_data["priority"] = post_data.priority
            
            # Always update timestamp
            update_data["updated_at"] = datetime.now()
            
            # Apply updates
            for field, value in update_data.items():
                setattr(existing_post, field, value)
            
            await session.commit()
            await session.refresh(existing_post)
            
            return PostResponse(
                id=existing_post.id,
                title=existing_post.title,
                content=existing_post.content,
                region=existing_post.region,
                theme=existing_post.theme,
                status=existing_post.status,
                image_url=existing_post.image_url,
                video_url=existing_post.video_url,
                scheduled_at=existing_post.scheduled_at,
                vk_group_id=existing_post.vk_group_id,
                telegram_chat_id=existing_post.telegram_chat_id,
                tags=existing_post.tags or [],
                priority=existing_post.priority,
                created_at=existing_post.created_at,
                updated_at=existing_post.updated_at
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating post {post_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update post: {str(e)}")

@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete a post."""
    try:
        if not async_session or not Post:
            raise HTTPException(status_code=500, detail="Database not available")
        
        async with async_session() as session:
            # Get existing post
            query = select(Post).where(Post.id == post_id)
            result = await session.execute(query)
            existing_post = result.scalar_one_or_none()
            
            if not existing_post:
                raise HTTPException(status_code=404, detail="Post not found")
            
            # Delete the post
            await session.delete(existing_post)
            await session.commit()
            
            return {"message": "Post deleted successfully"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting post {post_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete post: {str(e)}")

@router.post("/{post_id}/publish")
async def publish_post(
    post_id: int,
    publish_request: Optional[PublishRequest] = None,
    current_user: dict = Depends(get_current_user)
):
    """Publish a post immediately with enhanced options."""
    try:
        if not async_session or not Post:
            raise HTTPException(status_code=500, detail="Database not available")
        
        async with async_session() as session:
            # Get existing post
            query = select(Post).where(Post.id == post_id)
            result = await session.execute(query)
            existing_post = result.scalar_one_or_none()
            
            if not existing_post:
                raise HTTPException(status_code=404, detail="Post not found")
            
            # Update post status to publishing
            existing_post.status = "publishing"
            existing_post.updated_at = datetime.now()
            
            # If publish request provided, update targeting
            if publish_request:
                if publish_request.target_groups:
                    existing_post.vk_group_id = ",".join(publish_request.target_groups)
                if publish_request.delay_minutes > 0:
                    existing_post.scheduled_at = datetime.now() + timedelta(minutes=publish_request.delay_minutes)
                    existing_post.status = "scheduled"
            
            await session.commit()
            
            # TODO: Add Celery task for actual publishing
            # publish_post_task.delay(post_id, publish_request.dict() if publish_request else {})
            
            return {
                "message": "Post queued for publishing",
                "post_id": post_id,
                "status": existing_post.status,
                "scheduled_for": existing_post.scheduled_at.isoformat() if existing_post.scheduled_at else None
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error publishing post {post_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to publish post: {str(e)}")


@router.get("/stats/overview", response_model=PostStats)
async def get_post_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive post statistics."""
    try:
        if not async_session or not Post:
            # Return demo stats
            return PostStats(
                total_posts=42,
                published_posts=28,
                scheduled_posts=8,
                draft_posts=6,
                by_region={
                    "mi": 15,
                    "nolinsk": 12,
                    "arbazh": 8,
                    "kirs": 7
                },
                by_theme={
                    "novost": 18,
                    "prikol": 12,
                    "sosed": 8,
                    "kino": 4
                },
                by_status={
                    "published": 28,
                    "scheduled": 8,
                    "draft": 6
                }
            )
        
        async with async_session() as session:
            # Total posts
            total_query = select(func.count(Post.id))
            total_result = await session.execute(total_query)
            total_posts = total_result.scalar()
            
            # Posts by status
            status_query = select(Post.status, func.count(Post.id)).group_by(Post.status)
            status_result = await session.execute(status_query)
            status_stats = {row[0]: row[1] for row in status_result.fetchall()}
            
            # Posts by region
            region_query = select(Post.region, func.count(Post.id)).group_by(Post.region)
            region_result = await session.execute(region_query)
            region_stats = {row[0]: row[1] for row in region_result.fetchall()}
            
            # Posts by theme
            theme_query = select(Post.theme, func.count(Post.id)).group_by(Post.theme)
            theme_result = await session.execute(theme_query)
            theme_stats = {row[0]: row[1] for row in theme_result.fetchall()}
            
            return PostStats(
                total_posts=total_posts,
                published_posts=status_stats.get("published", 0),
                scheduled_posts=status_stats.get("scheduled", 0),
                draft_posts=status_stats.get("draft", 0),
                by_region=region_stats,
                by_theme=theme_stats,
                by_status=status_stats
            )
            
    except Exception as e:
        logger.error(f"Error getting post stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.post("/bulk/publish")
async def bulk_publish_posts(
    post_ids: List[int],
    publish_request: Optional[PublishRequest] = None,
    current_user: dict = Depends(get_current_user)
):
    """Publish multiple posts at once."""
    try:
        if not async_session or not Post:
            raise HTTPException(status_code=500, detail="Database not available")
        
        if len(post_ids) > 50:
            raise HTTPException(status_code=400, detail="Cannot publish more than 50 posts at once")
        
        async with async_session() as session:
            # Get all posts
            query = select(Post).where(Post.id.in_(post_ids))
            result = await session.execute(query)
            posts = result.scalars().all()
            
            if len(posts) != len(post_ids):
                found_ids = [p.id for p in posts]
                missing_ids = [pid for pid in post_ids if pid not in found_ids]
                raise HTTPException(
                    status_code=404, 
                    detail=f"Posts not found: {missing_ids}"
                )
            
            # Update all posts to publishing status
            published_count = 0
            for post in posts:
                if post.status in ["draft", "ready"]:
                    post.status = "publishing"
                    post.updated_at = datetime.now()
                    
                    # Apply publish settings if provided
                    if publish_request:
                        if publish_request.target_groups:
                            post.vk_group_id = ",".join(publish_request.target_groups)
                        if publish_request.delay_minutes > 0:
                            post.scheduled_at = datetime.now() + timedelta(
                                minutes=publish_request.delay_minutes + (published_count * 2)  # Stagger by 2 minutes
                            )
                            post.status = "scheduled"
                    
                    published_count += 1
            
            await session.commit()
            
            # TODO: Add Celery tasks for actual publishing
            # for post_id in post_ids:
            #     publish_post_task.delay(post_id, publish_request.dict() if publish_request else {})
            
            return {
                "message": f"Successfully queued {published_count} posts for publishing",
                "published_count": published_count,
                "total_requested": len(post_ids)
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error bulk publishing posts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to bulk publish: {str(e)}")


@router.post("/bulk/delete")
async def bulk_delete_posts(
    post_ids: List[int],
    current_user: dict = Depends(get_current_user)
):
    """Delete multiple posts at once."""
    try:
        if not async_session or not Post:
            raise HTTPException(status_code=500, detail="Database not available")
        
        if len(post_ids) > 100:
            raise HTTPException(status_code=400, detail="Cannot delete more than 100 posts at once")
        
        async with async_session() as session:
            # Get all posts to verify they exist
            query = select(Post).where(Post.id.in_(post_ids))
            result = await session.execute(query)
            posts = result.scalars().all()
            
            # Delete all found posts
            for post in posts:
                await session.delete(post)
            
            await session.commit()
            
            return {
                "message": f"Successfully deleted {len(posts)} posts",
                "deleted_count": len(posts),
                "total_requested": len(post_ids)
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error bulk deleting posts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to bulk delete: {str(e)}")

@router.get("/simple")
async def get_posts_simple():
    """Simple posts endpoint for the web interface."""
    try:
        # Return mock data for now - will be replaced with real data later
        mock_posts = [
            {
                "id": 1,
                "title": "Новости региона",
                "content": "Содержание поста о новостях региона...",
                "region": "Москва",
                "theme": "novost",
                "status": "published",
                "created_at": "2025-10-03T10:00:00Z",
                "published_at": "2025-10-03T10:05:00Z",
                "views": 1250,
                "likes": 45,
                "reposts": 12,
                "image_url": None,
                "video_url": None,
                "tags": ["новости", "регион"],
                "priority": 0
            },
            {
                "id": 2,
                "title": "Объявление",
                "content": "Важное объявление для жителей...",
                "region": "СПб",
                "theme": "obyavlenie",
                "status": "pending",
                "created_at": "2025-10-03T11:00:00Z",
                "published_at": None,
                "views": 0,
                "likes": 0,
                "reposts": 0,
                "image_url": None,
                "video_url": None,
                "tags": ["объявление"],
                "priority": 1
            },
            {
                "id": 3,
                "title": "Статья",
                "content": "Интересная статья на актуальную тему...",
                "region": "Екатеринбург",
                "theme": "statya",
                "status": "published",
                "created_at": "2025-10-03T09:00:00Z",
                "published_at": "2025-10-03T09:10:00Z",
                "views": 890,
                "likes": 32,
                "reposts": 8,
                "image_url": None,
                "video_url": None,
                "tags": ["статья", "анализ"],
                "priority": 0
            }
        ]
        
        return {
            "posts": mock_posts,
            "total": len(mock_posts),
            "limit": 10,
            "offset": 0,
            "has_more": False
        }
        
    except Exception as e:
        logger.error(f"Error getting simple posts: {e}")
        return {
            "posts": [],
            "total": 0,
            "limit": 10,
            "offset": 0,
            "has_more": False
        }