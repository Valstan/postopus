"""
Роутер для аналитики и статистики.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_

from .auth import get_current_user
from ..database import get_db
from ..models import Post, Group, User, Schedule

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_analytics(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение аналитики для дашборда."""
    try:
        # Общая статистика
        total_posts = db.query(Post).count()
        total_groups = db.query(Group).count()
        total_users = db.query(User).count()
        total_schedules = db.query(Schedule).count()
        
        # Статистика по статусам постов
        post_statuses = db.query(
            Post.status, 
            func.count(Post.id).label('count')
        ).group_by(Post.status).all()
        
        # Статистика по платформам
        platform_stats = db.query(
            Group.platform,
            func.count(Group.id).label('count')
        ).group_by(Group.platform).all()
        
        # Статистика по регионам
        region_stats = db.query(
            Post.region,
            func.count(Post.id).label('count')
        ).filter(Post.region.isnot(None)).group_by(Post.region).all()
        
        # Последние посты
        recent_posts = db.query(Post).order_by(desc(Post.created_at)).limit(10).all()
        
        # Активные группы
        active_groups = db.query(Group).filter(Group.is_active == True).all()
        
        return {
            "overview": {
                "total_posts": total_posts,
                "total_groups": total_groups,
                "total_users": total_users,
                "total_schedules": total_schedules
            },
            "post_statuses": [{"status": status, "count": count} for status, count in post_statuses],
            "platform_stats": [{"platform": platform, "count": count} for platform, count in platform_stats],
            "region_stats": [{"region": region, "count": count} for region, count in region_stats],
            "recent_posts": [
                {
                    "id": post.id,
                    "title": post.title,
                    "region": post.region,
                    "status": post.status,
                    "created_at": post.created_at
                } for post in recent_posts
            ],
            "active_groups": [
                {
                    "id": group.id,
                    "name": group.name,
                    "platform": group.platform,
                    "region": group.region
                } for group in active_groups
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard analytics: {e}")
        raise HTTPException(status_code=500, detail="Error getting analytics")

@router.get("/posts/statistics")
async def get_posts_statistics(
    days: int = Query(30, description="Количество дней для анализа"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение статистики постов за период."""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Посты за период
        posts_in_period = db.query(Post).filter(Post.created_at >= start_date).count()
        
        # Посты по дням
        daily_posts = db.query(
            func.date(Post.created_at).label('date'),
            func.count(Post.id).label('count')
        ).filter(Post.created_at >= start_date).group_by(
            func.date(Post.created_at)
        ).order_by('date').all()
        
        # Посты по регионам за период
        regional_posts = db.query(
            Post.region,
            func.count(Post.id).label('count')
        ).filter(
            and_(Post.created_at >= start_date, Post.region.isnot(None))
        ).group_by(Post.region).all()
        
        # Посты по статусам за период
        status_posts = db.query(
            Post.status,
            func.count(Post.id).label('count')
        ).filter(Post.created_at >= start_date).group_by(Post.status).all()
        
        return {
            "period": {
                "days": days,
                "start_date": start_date.isoformat(),
                "end_date": datetime.utcnow().isoformat()
            },
            "total_posts": posts_in_period,
            "daily_posts": [{"date": str(date), "count": count} for date, count in daily_posts],
            "regional_posts": [{"region": region, "count": count} for region, count in regional_posts],
            "status_posts": [{"status": status, "count": count} for status, count in status_posts]
        }
        
    except Exception as e:
        logger.error(f"Error getting posts statistics: {e}")
        raise HTTPException(status_code=500, detail="Error getting posts statistics")

@router.get("/groups/statistics")
async def get_groups_statistics(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение статистики групп."""
    try:
        # Общая статистика групп
        total_groups = db.query(Group).count()
        active_groups = db.query(Group).filter(Group.is_active == True).count()
        
        # Группы по платформам
        platform_groups = db.query(
            Group.platform,
            func.count(Group.id).label('count')
        ).group_by(Group.platform).all()
        
        # Группы по регионам
        regional_groups = db.query(
            Group.region,
            func.count(Group.id).label('count')
        ).filter(Group.region.isnot(None)).group_by(Group.region).all()
        
        # Группы с постами
        groups_with_posts = db.query(
            Group.id,
            Group.name,
            Group.platform,
            Group.region,
            func.count(Post.id).label('post_count')
        ).outerjoin(Post, Group.id == Post.vk_group_id).group_by(
            Group.id, Group.name, Group.platform, Group.region
        ).all()
        
        return {
            "overview": {
                "total_groups": total_groups,
                "active_groups": active_groups,
                "inactive_groups": total_groups - active_groups
            },
            "platform_groups": [{"platform": platform, "count": count} for platform, count in platform_groups],
            "regional_groups": [{"region": region, "count": count} for region, count in regional_groups],
            "groups_with_posts": [
                {
                    "id": group_id,
                    "name": name,
                    "platform": platform,
                    "region": region,
                    "post_count": post_count
                } for group_id, name, platform, region, post_count in groups_with_posts
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting groups statistics: {e}")
        raise HTTPException(status_code=500, detail="Error getting groups statistics")

@router.get("/regions")
async def get_regions(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение списка регионов с статистикой."""
    try:
        # Регионы из постов
        post_regions = db.query(
            Post.region,
            func.count(Post.id).label('post_count')
        ).filter(Post.region.isnot(None)).group_by(Post.region).all()
        
        # Регионы из групп
        group_regions = db.query(
            Group.region,
            func.count(Group.id).label('group_count')
        ).filter(Group.region.isnot(None)).group_by(Group.region).all()
        
        # Объединяем данные
        regions = {}
        for region, count in post_regions:
            if region not in regions:
                regions[region] = {"post_count": 0, "group_count": 0}
            regions[region]["post_count"] = count
        
        for region, count in group_regions:
            if region not in regions:
                regions[region] = {"post_count": 0, "group_count": 0}
            regions[region]["group_count"] = count
        
        return {
            "regions": [
                {
                    "name": region,
                    "post_count": data["post_count"],
                    "group_count": data["group_count"]
                } for region, data in regions.items()
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting regions: {e}")
        raise HTTPException(status_code=500, detail="Error getting regions")

@router.get("/search")
async def search_posts(
    q: str = Query(..., description="Поисковый запрос"),
    region: str = Query(None, description="Фильтр по региону"),
    status: str = Query(None, description="Фильтр по статусу"),
    limit: int = Query(50, description="Максимальное количество результатов"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Поиск постов по содержимому."""
    try:
        query = db.query(Post)
        
        # Поиск по содержимому
        if q:
            query = query.filter(
                Post.title.contains(q) | Post.content.contains(q)
            )
        
        # Фильтр по региону
        if region:
            query = query.filter(Post.region == region)
        
        # Фильтр по статусу
        if status:
            query = query.filter(Post.status == status)
        
        # Ограничение результатов
        results = query.limit(limit).all()
        
        return {
            "query": q,
            "filters": {
                "region": region,
                "status": status
            },
            "total": len(results),
            "results": [
                {
                    "id": post.id,
                    "title": post.title,
                    "content": post.content[:200] + "..." if len(post.content) > 200 else post.content,
                    "region": post.region,
                    "status": post.status,
                    "created_at": post.created_at
                } for post in results
            ]
        }
        
    except Exception as e:
        logger.error(f"Error searching posts: {e}")
        raise HTTPException(status_code=500, detail="Error searching posts")
