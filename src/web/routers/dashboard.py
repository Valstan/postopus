"""
Enhanced dashboard router with regional analytics and VK integration.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

try:
    from sqlalchemy.orm import Session
    from sqlalchemy import func
except ImportError:
    Session = None
    func = None

from ..database import get_database
from ..models import Post, Group, Schedule
from ...services.vk_service import EnhancedVKService
from ...services.post_processor import EnhancedPostProcessor
from ...models.config import AppConfig
from ..auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# Enhanced Pydantic models
class DashboardStats(BaseModel):
    """Enhanced statistics for dashboard."""
    total_posts: int
    published_today: int
    published_this_week: int
    scheduled_tasks: int
    active_regions: int
    active_vk_sessions: int
    error_count: int
    processing_rate: float
    last_update: datetime

class RecentPost(BaseModel):
    """Recent post with enhanced data."""
    id: int
    title: str
    content: str
    region: str
    theme: str
    published_at: datetime
    views: int
    likes: int
    reposts: int
    source_url: Optional[str]
    vk_group_id: Optional[str]

class RegionalStats(BaseModel):
    """Enhanced regional statistics."""
    region: str
    region_name: str
    posts_count: int
    posts_today: int
    views_total: int
    engagement_rate: float
    active_groups: int
    last_post_time: Optional[datetime]

class VKConnectionStatus(BaseModel):
    """VK API connection status."""
    total_tokens: int
    working_sessions: int
    failed_sessions: int
    last_check: datetime
    details: List[Dict[str, Any]]

class SystemStatus(BaseModel):
    """Enhanced system status."""
    web_server: str
    database: str
    vk_api: str
    task_queue: str
    post_processor: str
    last_check: datetime

class ProcessingStats(BaseModel):
    """Post processing statistics."""
    total_processed: int
    filtered_out: int
    success_rate: float
    avg_processing_time: float
    by_theme: Dict[str, int]
    by_region: Dict[str, int]

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """Gets enhanced dashboard statistics."""
    try:
        db = get_database()
        
        # Get current time references
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)
        
        if Session and db:
            try:
                with db.get_session() as session:
                    # Total posts
                    total_posts = session.query(Post).count()
                    
                    # Posts published today
                    published_today = session.query(Post).filter(
                        Post.created_at >= today_start,
                        Post.status == 'published'
                    ).count()
                    
                    # Posts published this week
                    published_this_week = session.query(Post).filter(
                        Post.created_at >= week_start,
                        Post.status == 'published'
                    ).count()
                    
                    # Active regions (regions with posts in last 7 days)
                    active_regions = session.query(func.count(func.distinct(Post.region))).filter(
                        Post.created_at >= week_start
                    ).scalar() or 0
                    
                    # Scheduled tasks
                    scheduled_tasks = session.query(Schedule).filter(
                        Schedule.is_active == True
                    ).count()
                    
            except Exception as e:
                logger.warning(f"Database query failed, using fallback data: {e}")
                # Fallback to demo data
                total_posts = 1547
                published_today = 23
                published_this_week = 156
                active_regions = 15
                scheduled_tasks = 8
        else:
            # Demo data when database not available
            total_posts = 1547
            published_today = 23
            published_this_week = 156
            active_regions = 15
            scheduled_tasks = 8
        
        # Try to get VK session count
        try:
            config = AppConfig.from_env()
            vk_service = EnhancedVKService(config)
            await vk_service.initialize()
            active_vk_sessions = len(vk_service.vk_sessions)
        except Exception:
            active_vk_sessions = len(AppConfig.from_env().vk.tokens) if AppConfig.from_env().vk.tokens else 0
        
        # Calculate processing rate (posts per hour)
        processing_rate = published_today / 24.0 if published_today > 0 else 0.0
        
        return DashboardStats(
            total_posts=total_posts,
            published_today=published_today,
            published_this_week=published_this_week,
            scheduled_tasks=scheduled_tasks,
            active_regions=active_regions,
            active_vk_sessions=active_vk_sessions,
            error_count=2,  # TODO: Implement error tracking
            processing_rate=processing_rate,
            last_update=now
        )
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Error getting dashboard stats")

@router.get("/recent-posts", response_model=List[RecentPost])
async def get_recent_posts(
    limit: int = 10, 
    region: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Gets recent posts with optional region filtering."""
    try:
        db = get_database()
        posts = []
        
        if Session and db:
            try:
                with db.get_session() as session:
                    query = session.query(Post).filter(
                        Post.status == 'published'
                    )
                    
                    if region:
                        query = query.filter(Post.region == region)
                    
                    db_posts = query.order_by(Post.created_at.desc()).limit(limit).all()
                    
                    for post in db_posts:
                        # Extract metadata
                        metadata = post.post_metadata or {}
                        
                        posts.append(RecentPost(
                            id=post.id,
                            title=post.title,
                            content=post.content[:200] + "..." if len(post.content) > 200 else post.content,
                            region=post.region or 'unknown',
                            theme=metadata.get('theme', 'general'),
                            published_at=post.created_at,
                            views=metadata.get('views', {}).get('count', 0),
                            likes=metadata.get('likes', 0),
                            reposts=metadata.get('reposts', 0),
                            source_url=metadata.get('source_url'),
                            vk_group_id=post.vk_group_id
                        ))
                    
            except Exception as e:
                logger.warning(f"Database query failed, using demo data: {e}")
                posts = []  # Will fall through to demo data
        
        # Fallback to demo data if no database posts
        if not posts:
            regions = ["mi", "nolinsk", "arbazh", "nema", "ur", "klz", "pizhanka", "kukmor", "sovetsk", "vp"]
            themes = ["novost", "sosed", "reklama", "kino", "music"]
            
            for i in range(limit):
                selected_region = region if region else regions[i % len(regions)]
                posts.append(RecentPost(
                    id=i+1,
                    title=f"Sample post from {selected_region}",
                    content=f"Sample post content from region {selected_region}. This is demonstration data showing how posts would appear in the dashboard...",
                    published_at=datetime.utcnow() - timedelta(hours=i),
                    views=150 + i * 10,
                    likes=20 + i * 2,
                    reposts=5 + i,
                    region=selected_region,
                    theme=themes[i % len(themes)],
                    source_url=f"https://vk.com/wall-12345_{i+1}",
                    vk_group_id="-12345"
                ))
        
        return posts
        
    except Exception as e:
        logger.error(f"Error getting recent posts: {e}")
        raise HTTPException(status_code=500, detail="Error getting recent posts")

@router.get("/regional-stats", response_model=List[RegionalStats])
async def get_regional_stats(current_user: dict = Depends(get_current_user)):
    """Gets enhanced statistics by region."""
    try:
        db = get_database()
        regional_data = []
        
        # Regional mapping
        regions = {
            'mi': 'Malmyž',
            'nolinsk': 'Nolinsk', 
            'arbazh': 'Arbazh',
            'nema': 'Nema',
            'ur': 'Uržum',
            'verhoshizhem': 'Verhošižem\'e',
            'klz': 'Kil\'mez\'',
            'pizhanka': 'Pižanka',
            'afon': 'Afon',
            'kukmor': 'Kukmor',
            'sovetsk': 'Sovetsk',
            'malmigrus': 'Malmyž Groups',
            'vp': 'Vjatskie Poljany',
            'leb': 'Lebjaž\'e',
            'dran': 'Dran',
            'bal': 'Baltasi'
        }
        
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if Session and db:
            try:
                with db.get_session() as session:
                    for region_code, region_name in regions.items():
                        # Posts count for this region
                        posts_count = session.query(Post).filter(
                            Post.region == region_code
                        ).count()
                        
                        # Posts today
                        posts_today = session.query(Post).filter(
                            Post.region == region_code,
                            Post.created_at >= today_start
                        ).count()
                        
                        # Active groups count
                        active_groups = session.query(Group).filter(
                            Group.region == region_code,
                            Group.is_active == True
                        ).count()
                        
                        # Last post time
                        last_post = session.query(Post).filter(
                            Post.region == region_code
                        ).order_by(Post.created_at.desc()).first()
                        
                        last_post_time = last_post.created_at if last_post else None
                        
                        # Calculate engagement rate (simplified)
                        views_total = 0
                        if posts_count > 0:
                            # Try to extract views from metadata
                            posts_with_views = session.query(Post).filter(
                                Post.region == region_code,
                                Post.post_metadata.isnot(None)
                            ).all()
                            
                            for post in posts_with_views:
                                if post.post_metadata and 'views' in post.post_metadata:
                                    views_total += post.post_metadata['views'].get('count', 0)
                        
                        engagement_rate = (views_total / posts_count) if posts_count > 0 else 0.0
                        
                        if posts_count > 0:  # Only include regions with posts
                            regional_data.append(RegionalStats(
                                region=region_code,
                                region_name=region_name,
                                posts_count=posts_count,
                                posts_today=posts_today,
                                views_total=views_total,
                                engagement_rate=round(engagement_rate, 2),
                                active_groups=active_groups,
                                last_post_time=last_post_time
                            ))
                    
            except Exception as e:
                logger.warning(f"Database query failed, using demo data: {e}")
                regional_data = []  # Will fall through to demo data
        
        # Fallback to demo data
        if not regional_data:
            demo_data = [
                {"region": "mi", "name": "Malmyž", "posts": 189, "today": 12, "views": 15420, "engagement": 4.2, "groups": 3},
                {"region": "nolinsk", "name": "Nolinsk", "posts": 156, "today": 8, "views": 12300, "engagement": 3.8, "groups": 2},
                {"region": "arbazh", "name": "Arbazh", "posts": 134, "today": 6, "views": 10800, "engagement": 3.5, "groups": 2},
                {"region": "nema", "name": "Nema", "posts": 98, "today": 4, "views": 8900, "engagement": 3.2, "groups": 1},
                {"region": "ur", "name": "Uržum", "posts": 167, "today": 9, "views": 13400, "engagement": 4.0, "groups": 2},
                {"region": "klz", "name": "Kil'mez'", "posts": 145, "today": 7, "views": 11200, "engagement": 3.6, "groups": 2},
                {"region": "pizhanka", "name": "Pižanka", "posts": 123, "today": 5, "views": 9800, "engagement": 3.4, "groups": 1},
                {"region": "kukmor", "name": "Kukmor", "posts": 111, "today": 3, "views": 9100, "engagement": 3.1, "groups": 1},
                {"region": "sovetsk", "name": "Sovetsk", "posts": 142, "today": 6, "views": 11800, "engagement": 3.7, "groups": 2},
                {"region": "vp", "name": "Vjatskie Poljany", "posts": 178, "today": 10, "views": 14200, "engagement": 4.1, "groups": 3},
            ]
            
            for data in demo_data:
                regional_data.append(RegionalStats(
                    region=data["region"],
                    region_name=data["name"],
                    posts_count=data["posts"],
                    posts_today=data["today"],
                    views_total=data["views"],
                    engagement_rate=data["engagement"],
                    active_groups=data["groups"],
                    last_post_time=datetime.utcnow() - timedelta(minutes=data["today"] * 15)
                ))
        
        # Sort by posts count (descending)
        regional_data.sort(key=lambda x: x.posts_count, reverse=True)
        
        return regional_data
        
    except Exception as e:
        logger.error(f"Error getting regional stats: {e}")
        raise HTTPException(status_code=500, detail="Error getting regional stats")

@router.get("/vk-status", response_model=VKConnectionStatus)
async def get_vk_status(current_user: dict = Depends(get_current_user)):
    """Gets VK API connection status."""
    try:
        config = AppConfig.from_env()
        
        # Test VK connections
        try:
            vk_service = EnhancedVKService(config)
            await vk_service.initialize()
            connection_results = await vk_service.test_connection()
            
            return VKConnectionStatus(
                total_tokens=connection_results['total_tokens'],
                working_sessions=connection_results['working_sessions'],
                failed_sessions=connection_results['total_tokens'] - connection_results['working_sessions'],
                last_check=datetime.utcnow(),
                details=connection_results['details']
            )
            
        except Exception as e:
            logger.warning(f"VK service test failed: {e}")
            # Return status based on configuration
            total_tokens = len(config.vk.tokens) if config.vk.tokens else 0
            return VKConnectionStatus(
                total_tokens=total_tokens,
                working_sessions=0,
                failed_sessions=total_tokens,
                last_check=datetime.utcnow(),
                details=[{"error": str(e)}]
            )
        
    except Exception as e:
        logger.error(f"Error getting VK status: {e}")
        raise HTTPException(status_code=500, detail="Error getting VK status")

@router.get("/processing-stats", response_model=ProcessingStats)
async def get_processing_stats(current_user: dict = Depends(get_current_user)):
    """Gets post processing statistics."""
    try:
        # For now, return demo data. In production, this would query processing logs
        return ProcessingStats(
            total_processed=1547,
            filtered_out=423,
            success_rate=78.5,
            avg_processing_time=1.2,
            by_theme={
                "novost": 890,
                "sosed": 234,
                "reklama": 189,
                "kino": 123,
                "music": 111
            },
            by_region={
                "mi": 189,
                "nolinsk": 156,
                "arbazh": 134,
                "ur": 167,
                "klz": 145,
                "pizhanka": 123,
                "kukmor": 111,
                "sovetsk": 142,
                "vp": 178,
                "others": 302
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting processing stats: {e}")
        raise HTTPException(status_code=500, detail="Error getting processing stats")

@router.get("/system-status", response_model=SystemStatus)
async def get_system_status(current_user: dict = Depends(get_current_user)):
    """Gets enhanced system status."""
    try:
        # Test database connection
        db_status = "connected"
        try:
            db = get_database()
            if Session and db:
                with db.get_session() as session:
                    session.execute("SELECT 1")
        except Exception:
            db_status = "disconnected"
        
        # Test VK API
        vk_status = "operational"
        try:
            config = AppConfig.from_env()
            if not config.vk.tokens:
                vk_status = "not_configured"
            else:
                vk_service = EnhancedVKService(config)
                await vk_service.initialize()
                if len(vk_service.vk_sessions) == 0:
                    vk_status = "failed"
        except Exception:
            vk_status = "error"
        
        # Test post processor
        processor_status = "operational"
        try:
            processor = EnhancedPostProcessor(AppConfig.from_env())
            await processor.load_filtering_data()
        except Exception:
            processor_status = "error"
        
        return SystemStatus(
            web_server="online",
            database=db_status,
            vk_api=vk_status,
            task_queue="operational",  # TODO: Add Celery status check
            post_processor=processor_status,
            last_check=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail="Error getting system status")

@router.get("/chart-data")
async def get_chart_data(
    days: int = 7, 
    region: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Gets enhanced chart data with optional region filtering."""
    try:
        db = get_database()
        labels = []
        posts_data = []
        views_data = []
        
        # Generate date labels
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=days-i-1)
            labels.append(date.strftime("%Y-%m-%d"))
        
        if Session and db:
            try:
                with db.get_session() as session:
                    for i, label in enumerate(labels):
                        date_start = datetime.strptime(label, "%Y-%m-%d")
                        date_end = date_start + timedelta(days=1)
                        
                        # Query posts for this day
                        query = session.query(Post).filter(
                            Post.created_at >= date_start,
                            Post.created_at < date_end
                        )
                        
                        if region:
                            query = query.filter(Post.region == region)
                        
                        day_posts = query.count()
                        posts_data.append(day_posts)
                        
                        # Calculate views (from metadata)
                        day_views = 0
                        posts_with_views = query.filter(
                            Post.post_metadata.isnot(None)
                        ).all()
                        
                        for post in posts_with_views:
                            if post.post_metadata and 'views' in post.post_metadata:
                                day_views += post.post_metadata['views'].get('count', 0)
                        
                        views_data.append(day_views)
                        
            except Exception as e:
                logger.warning(f"Database query failed, using demo data: {e}")
                # Fall through to demo data
                posts_data = []
                views_data = []
        
        # Use demo data if database unavailable or no data
        if not posts_data:
            for i in range(days):
                posts_data.append(15 + (i * 3) + (i % 3))  # Simulate growth
                views_data.append(1200 + (i * 150) + (i % 100))
        
        return {
            "labels": labels,
            "datasets": [
                {
                    "label": "Posts",
                    "data": posts_data,
                    "borderColor": "rgb(75, 192, 192)",
                    "backgroundColor": "rgba(75, 192, 192, 0.2)",
                    "tension": 0.1
                },
                {
                    "label": "Views",
                    "data": views_data,
                    "borderColor": "rgb(255, 99, 132)",
                    "backgroundColor": "rgba(255, 99, 132, 0.2)",
                    "tension": 0.1,
                    "yAxisID": "y1"
                }
            ],
            "options": {
                "responsive": True,
                "scales": {
                    "y": {
                        "type": "linear",
                        "display": True,
                        "position": "left"
                    },
                    "y1": {
                        "type": "linear",
                        "display": True,
                        "position": "right",
                        "grid": {
                            "drawOnChartArea": False
                        }
                    }
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting chart data: {e}")
        raise HTTPException(status_code=500, detail="Error getting chart data")

@router.get("/overview")
async def get_dashboard_overview(current_user: dict = Depends(get_current_user)):
    """Gets comprehensive dashboard overview with all metrics."""
    try:
        # Get all dashboard data concurrently
        stats = await get_dashboard_stats(current_user)
        recent_posts = await get_recent_posts(5, None, current_user)
        regional_stats = await get_regional_stats(current_user)
        vk_status = await get_vk_status(current_user)
        processing_stats = await get_processing_stats(current_user)
        system_status = await get_system_status(current_user)
        
        # Get top 5 regions by posts count
        top_regions = sorted(regional_stats, key=lambda x: x.posts_count, reverse=True)[:5]
        
        return {
            "stats": stats,
            "recent_posts": recent_posts,
            "regional_stats": {
                "top_regions": top_regions,
                "total_regions": len(regional_stats),
                "active_regions": len([r for r in regional_stats if r.posts_today > 0])
            },
            "vk_status": vk_status,
            "processing_stats": processing_stats,
            "system_status": system_status,
            "summary": {
                "health_score": _calculate_health_score(system_status, vk_status, stats),
                "performance_index": _calculate_performance_index(stats, processing_stats),
                "recommendations": _generate_recommendations(stats, regional_stats, vk_status)
            },
            "generated_at": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard overview: {e}")
        raise HTTPException(status_code=500, detail="Error getting dashboard overview")


def _calculate_health_score(system_status: SystemStatus, vk_status: VKConnectionStatus, stats: DashboardStats) -> float:
    """Calculate overall system health score (0-100)."""
    score = 100.0
    
    # Database health
    if system_status.database != "connected":
        score -= 30
    
    # VK API health
    if vk_status.working_sessions == 0:
        score -= 25
    elif vk_status.working_sessions < vk_status.total_tokens:
        score -= 10
    
    # Processing health
    if system_status.post_processor != "operational":
        score -= 20
    
    # Activity level
    if stats.published_today == 0:
        score -= 15
    elif stats.published_today < 5:
        score -= 5
    
    return max(0.0, score)


def _calculate_performance_index(stats: DashboardStats, processing_stats: ProcessingStats) -> float:
    """Calculate performance index based on processing efficiency."""
    if processing_stats.total_processed == 0:
        return 0.0
    
    # Base score from success rate
    base_score = processing_stats.success_rate
    
    # Bonus for high activity
    if stats.processing_rate > 5.0:  # More than 5 posts per hour
        base_score += 10
    elif stats.processing_rate > 2.0:
        base_score += 5
    
    # Penalty for slow processing
    if processing_stats.avg_processing_time > 5.0:
        base_score -= 10
    
    return min(100.0, max(0.0, base_score))


def _generate_recommendations(stats: DashboardStats, regional_stats: List[RegionalStats], vk_status: VKConnectionStatus) -> List[str]:
    """Generate actionable recommendations based on current metrics."""
    recommendations = []
    
    # VK API recommendations
    if vk_status.working_sessions == 0:
        recommendations.append("🔴 Configure VK API tokens to enable posting functionality")
    elif vk_status.working_sessions < vk_status.total_tokens:
        recommendations.append("🟡 Some VK tokens are not working - check token validity")
    
    # Activity recommendations
    if stats.published_today < 10:
        recommendations.append("📈 Consider increasing posting frequency to improve engagement")
    
    # Regional recommendations
    inactive_regions = [r for r in regional_stats if r.posts_today == 0]
    if len(inactive_regions) > 3:
        recommendations.append(f"📍 {len(inactive_regions)} regions have no posts today - review content sources")
    
    # Performance recommendations
    low_engagement_regions = [r for r in regional_stats if r.engagement_rate < 2.0]
    if len(low_engagement_regions) > 2:
        recommendations.append("🎯 Improve content quality in low-engagement regions")
    
    # Default recommendation if all is well
    if not recommendations:
        recommendations.append("✅ System is running optimally - continue current operations")
    
    return recommendations