"""
Legacy Statistics Router — API эндпоинты для отображения
статистики работы портированных legacy модулей в веб-интерфейсе master.
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from web.auth import get_current_user
from web.database import SessionLocal
from web.data_manager import PostopusDataManager

router = APIRouter(prefix="/api/legacy", tags=["legacy"])


# In-memory cache для последних результатов обработки
_last_processing_results: dict[str, Any] = {}


@router.get("/processing-stats")
async def get_processing_stats(current_user: Any = Depends(get_current_user)):
    """
    Статистика последней обработки legacy модулями.
    Показывает статус по регионам и тематикам.
    """
    return {
        "last_update": datetime.now().isoformat(),
        "status": "legacy_integration_in_progress",
        "message": "Legacy модули портированы. Celery tasks настраиваются.",
        "migrated_modules": {
            "utils": ["lip_of_post", "clear_copy_history", "url_of_post",
                      "search_text", "text_to_rafinad", "clear_text",
                      "send_error", "post_popularity", "is_advertisement"],
            "rw": ["get_msg"],
            "tasks": ["legacy_tasks.py"],
        },
    }


@router.get("/recent-digests")
async def get_recent_digests(
    limit: int = 20,
    current_user: Any = Depends(get_current_user),
):
    """
    Последние опубликованные дайджесты через legacy систему.
    """
    db = SessionLocal()
    try:
        manager = PostopusDataManager(db)
        posts = manager.get_recent_posts(limit=limit)
        return {"digests": posts, "total": len(posts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/region/{region_name}/stats")
async def get_region_stats(
    region_name: str,
    current_user: Any = Depends(get_current_user),
):
    """
    Статистика обработки конкретного региона legacy модулями.
    """
    return {
        "region": region_name,
        "status": "pending_migration",
        "message": f"Статистика для региона '{region_name}' будет доступна после завершения миграции",
    }


@router.get("/theme/{theme}/stats")
async def get_theme_stats(
    theme: str,
    current_user: Any = Depends(get_current_user),
):
    """
    Статистика обработки тематики legacy модулями.
    """
    return {
        "theme": theme,
        "status": "pending_migration",
        "message": f"Статистика для тематики '{theme}' будет доступна после завершения миграции",
    }
