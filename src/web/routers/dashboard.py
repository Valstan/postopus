"""
Роутер для дашборда.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..database import get_database
from .auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

class DashboardStats(BaseModel):
    """Статистика для дашборда."""
    total_posts: int
    published_today: int
    scheduled_tasks: int
    active_sessions: int
    error_count: int
    last_update: datetime

class RecentPost(BaseModel):
    """Недавний пост."""
    id: str
    text: str
    published_at: datetime
    views: int
    likes: int
    reposts: int

class DashboardData(BaseModel):
    """Данные для дашборда."""
    stats: DashboardStats
    recent_posts: List[RecentPost]
    chart_data: Dict[str, Any]

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Получает статистику для дашборда."""
    try:
        # Получаем статистику из базы данных
        posts_collection = db.get_collection("posts")
        tasks_collection = db.get_collection("tasks")
        sessions_collection = db.get_collection("sessions")
        
        # Общее количество постов
        total_posts = await posts_collection.count_documents({})
        
        # Посты за сегодня
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        published_today = await posts_collection.count_documents({
            "published_at": {"$gte": today}
        })
        
        # Запланированные задачи
        scheduled_tasks = await tasks_collection.count_documents({
            "status": "scheduled"
        })
        
        # Активные сессии
        active_sessions = await sessions_collection.count_documents({
            "status": "active"
        })
        
        # Ошибки за последние 24 часа
        yesterday = datetime.now() - timedelta(days=1)
        error_count = await tasks_collection.count_documents({
            "status": "error",
            "created_at": {"$gte": yesterday}
        })
        
        return DashboardStats(
            total_posts=total_posts,
            published_today=published_today,
            scheduled_tasks=scheduled_tasks,
            active_sessions=active_sessions,
            error_count=error_count,
            last_update=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Error getting dashboard stats")

@router.get("/recent-posts", response_model=List[RecentPost])
async def get_recent_posts(
    limit: int = 10,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Получает недавние посты."""
    try:
        posts_collection = db.get_collection("posts")
        
        # Получаем последние посты
        posts = await posts_collection.find(
            {},
            {"_id": 0, "id": 1, "text": 1, "published_at": 1, "views": 1, "likes": 1, "reposts": 1}
        ).sort("published_at", -1).limit(limit).to_list(length=limit)
        
        return [
            RecentPost(
                id=post["id"],
                text=post["text"][:100] + "..." if len(post["text"]) > 100 else post["text"],
                published_at=post["published_at"],
                views=post.get("views", 0),
                likes=post.get("likes", 0),
                reposts=post.get("reposts", 0)
            )
            for post in posts
        ]
        
    except Exception as e:
        logger.error(f"Error getting recent posts: {e}")
        raise HTTPException(status_code=500, detail="Error getting recent posts")

@router.get("/chart-data")
async def get_chart_data(
    days: int = 7,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Получает данные для графиков."""
    try:
        posts_collection = db.get_collection("posts")
        
        # Получаем данные за последние N дней
        start_date = datetime.now() - timedelta(days=days)
        
        # Группируем по дням
        pipeline = [
            {
                "$match": {
                    "published_at": {"$gte": start_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$published_at"},
                        "month": {"$month": "$published_at"},
                        "day": {"$dayOfMonth": "$published_at"}
                    },
                    "count": {"$sum": 1},
                    "total_views": {"$sum": "$views"},
                    "total_likes": {"$sum": "$likes"},
                    "total_reposts": {"$sum": "$reposts"}
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]
        
        chart_data = await posts_collection.aggregate(pipeline).to_list(length=None)
        
        # Форматируем данные для фронтенда
        labels = []
        posts_data = []
        views_data = []
        likes_data = []
        reposts_data = []
        
        for item in chart_data:
            date_str = f"{item['_id']['year']}-{item['_id']['month']:02d}-{item['_id']['day']:02d}"
            labels.append(date_str)
            posts_data.append(item["count"])
            views_data.append(item["total_views"])
            likes_data.append(item["total_likes"])
            reposts_data.append(item["total_reposts"])
        
        return {
            "labels": labels,
            "datasets": [
                {
                    "label": "Посты",
                    "data": posts_data,
                    "borderColor": "rgb(75, 192, 192)",
                    "backgroundColor": "rgba(75, 192, 192, 0.2)"
                },
                {
                    "label": "Просмотры",
                    "data": views_data,
                    "borderColor": "rgb(255, 99, 132)",
                    "backgroundColor": "rgba(255, 99, 132, 0.2)"
                },
                {
                    "label": "Лайки",
                    "data": likes_data,
                    "borderColor": "rgb(54, 162, 235)",
                    "backgroundColor": "rgba(54, 162, 235, 0.2)"
                },
                {
                    "label": "Репосты",
                    "data": reposts_data,
                    "borderColor": "rgb(255, 205, 86)",
                    "backgroundColor": "rgba(255, 205, 86, 0.2)"
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting chart data: {e}")
        raise HTTPException(status_code=500, detail="Error getting chart data")

@router.get("/", response_model=DashboardData)
async def get_dashboard_data(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Получает все данные для дашборда."""
    try:
        stats = await get_dashboard_stats(current_user, db)
        recent_posts = await get_recent_posts(10, current_user, db)
        chart_data = await get_chart_data(7, current_user, db)
        
        return DashboardData(
            stats=stats,
            recent_posts=recent_posts,
            chart_data=chart_data
        )
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Error getting dashboard data")
