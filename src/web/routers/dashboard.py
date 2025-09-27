"""
Simplified dashboard router for demonstration.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models
class DashboardStats(BaseModel):
    """Statistics for dashboard."""
    total_posts: int
    published_today: int
    scheduled_tasks: int
    active_sessions: int
    error_count: int
    last_update: datetime

class RecentPost(BaseModel):
    """Recent post."""
    id: str
    text: str
    published_at: datetime
    views: int
    likes: int
    reposts: int
    region: str

class RegionalStats(BaseModel):
    """Regional statistics."""
    region: str
    posts_count: int
    views_total: int
    engagement_rate: float

class SystemStatus(BaseModel):
    """System status."""
    web_server: str
    database: str
    task_queue: str
    last_check: datetime

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Gets dashboard statistics."""
    try:
        # Demo data for visualization
        return DashboardStats(
            total_posts=1547,
            published_today=23,
            scheduled_tasks=8,
            active_sessions=15,
            error_count=2,
            last_update=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Error getting dashboard stats")

@router.get("/recent-posts", response_model=List[RecentPost])
async def get_recent_posts(limit: int = 10):
    """Gets recent posts."""
    try:
        # Demo data
        regions = ["mi", "nolinsk", "arbazh", "nema", "ur", "klz", "pizhanka"]
        posts = []
        
        for i in range(limit):
            posts.append(RecentPost(
                id=f"post_{i+1}",
                text=f"Sample post content from region {regions[i % len(regions)]}...",
                published_at=datetime.now() - timedelta(hours=i),
                views=150 + i * 10,
                likes=20 + i * 2,
                reposts=5 + i,
                region=regions[i % len(regions)]
            ))
        
        return posts
        
    except Exception as e:
        logger.error(f"Error getting recent posts: {e}")
        raise HTTPException(status_code=500, detail="Error getting recent posts")

@router.get("/regional-stats", response_model=List[RegionalStats])
async def get_regional_stats():
    """Gets statistics by region."""
    try:
        regions_data = [
            {"region": "Malmyž (mi)", "posts": 189, "views": 15420, "engagement": 4.2},
            {"region": "Nolinsk", "posts": 156, "views": 12300, "engagement": 3.8},
            {"region": "Arbazh", "posts": 134, "views": 10800, "engagement": 3.5},
            {"region": "Nema", "posts": 98, "views": 8900, "engagement": 3.2},
            {"region": "Uržum", "posts": 167, "views": 13400, "engagement": 4.0},
            {"region": "Kil'mez'", "posts": 145, "views": 11200, "engagement": 3.6},
            {"region": "Pižanka", "posts": 123, "views": 9800, "engagement": 3.4},
            {"region": "Kukmor", "posts": 111, "views": 9100, "engagement": 3.1},
            {"region": "Sovetsk", "posts": 142, "views": 11800, "engagement": 3.7},
            {"region": "Vj. Poljany", "posts": 178, "views": 14200, "engagement": 4.1},
        ]
        
        return [
            RegionalStats(
                region=data["region"],
                posts_count=data["posts"],
                views_total=data["views"],
                engagement_rate=data["engagement"]
            )
            for data in regions_data
        ]
        
    except Exception as e:
        logger.error(f"Error getting regional stats: {e}")
        raise HTTPException(status_code=500, detail="Error getting regional stats")

@router.get("/chart-data")
async def get_chart_data(days: int = 7):
    """Gets data for charts."""
    try:
        # Generate sample chart data
        labels = []
        posts_data = []
        views_data = []
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i-1)
            labels.append(date.strftime("%Y-%m-%d"))
            posts_data.append(15 + (i * 3) + (i % 3))  # Simulate growth
            views_data.append(1200 + (i * 150) + (i % 100))
        
        return {
            "labels": labels,
            "datasets": [
                {
                    "label": "Posts",
                    "data": posts_data,
                    "borderColor": "rgb(75, 192, 192)",
                    "backgroundColor": "rgba(75, 192, 192, 0.2)"
                },
                {
                    "label": "Views",
                    "data": views_data,
                    "borderColor": "rgb(255, 99, 132)",
                    "backgroundColor": "rgba(255, 99, 132, 0.2)"
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting chart data: {e}")
        raise HTTPException(status_code=500, detail="Error getting chart data")

@router.get("/system-status", response_model=SystemStatus)
async def get_system_status():
    """Gets system status."""
    try:
        return SystemStatus(
            web_server="online",
            database="connected",
            task_queue="operational",
            last_check=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail="Error getting system status")

@router.get("/overview")
async def get_dashboard_overview():
    """Gets complete dashboard overview."""
    try:
        stats = await get_dashboard_stats()
        recent_posts = await get_recent_posts(5)
        regional_stats = await get_regional_stats()
        system_status = await get_system_status()
        
        return {
            "stats": stats,
            "recent_posts": recent_posts,
            "regional_stats": regional_stats[:5],  # Top 5 regions
            "system_status": system_status,
            "generated_at": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard overview: {e}")
        raise HTTPException(status_code=500, detail="Error getting dashboard overview")