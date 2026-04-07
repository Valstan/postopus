"""
Legacy Runner Router — API для ручного запуска legacy обработки
и мониторинга выполнения.
"""

from typing import Any, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from web.auth import get_current_user

router = APIRouter(prefix="/api/legacy", tags=["legacy-runner"])

# In-memory tracking of running tasks
_active_tasks: dict[str, dict] = {}


@router.post("/run")
async def run_legacy_session(
    region_name: str,
    theme: str,
    bags: str = "0",
    background_tasks: BackgroundTasks = None,
    current_user: Any = Depends(get_current_user),
):
    """
    Запустить обработку сессии (аналог start.py region_theme).

    Args:
        region_name: Название региона
        theme: Тематика
        bags: Режим фильтров (0-5)
    """
    task_id = f"{region_name}_{theme}"

    _active_tasks[task_id] = {
        "status": "queued",
        "region": region_name,
        "theme": theme,
    }

    if background_tasks:
        # Запуск в фоне (для dev)
        background_tasks.add_task(_execute_legacy_session, task_id, region_name, theme, bags)
        return {"task_id": task_id, "status": "queued"}
    else:
        # В production используется Celery task
        return {
            "task_id": task_id,
            "status": "use_celery",
            "message": "Для production используйте Celery task: tasks.legacy_tasks.run_legacy_session_task",
        }


@router.post("/run-packet/{theme}")
async def run_legacy_packet(
    theme: str,
    background_tasks: BackgroundTasks = None,
    current_user: Any = Depends(get_current_user),
):
    """
    Запустить обработку темы по всем регионам (аналог start_paket.py theme).
    """
    task_id = f"packet_{theme}"

    if background_tasks:
        background_tasks.add_task(_execute_legacy_packet, task_id, theme)
        return {"task_id": task_id, "status": "queued"}
    else:
        return {
            "task_id": task_id,
            "status": "use_celery",
            "message": "Для production используйте Celery task: tasks.legacy_tasks.run_legacy_packet_task",
        }


@router.get("/status")
async def get_legacy_status(current_user: Any = Depends(get_current_user)):
    """
    Статус legacy интеграции.
    """
    return {
        "migration_status": "in_progress",
        "migrated_modules": {
            "utils": 11,  # Количество портированных утилит
            "rw": 1,
            "tasks": 1,
            "web_routers": 2,
        },
        "pending_modules": {
            "rw": ["get_attach", "post_msg", "posting_post", "get_session",
                   "get_session_vk_api", "publish_stats"],
            "sort": ["sort_old_date", "sort_po_foto", "sort_po_video"],
            "control": ["parser", "control", "oblast_novost", "karavan",
                       "sosed", "repost_me", "repost_oleny", "repost_reklama",
                       "repost_kultpodved", "repost_oblast_setka", "post_to_telega"],
        },
        "active_tasks": _active_tasks,
    }


async def _execute_legacy_session(task_id: str, region: str, theme: str, bags: str):
    """Фоновое выполнение legacy сессии."""
    try:
        _active_tasks[task_id]["status"] = "running"
        from src.legacy.legacy_runner import run_session
        result = run_session(f"{region}_{theme}", bags=bags)
        _active_tasks[task_id] = {
            "status": "completed",
            "result": result,
        }
    except Exception as e:
        _active_tasks[task_id] = {
            "status": "failed",
            "error": str(e),
        }


async def _execute_legacy_packet(task_id: str, theme: str):
    """Фоновое выполнение legacy packet."""
    try:
        _active_tasks[task_id]["status"] = "running"
        from src.legacy.legacy_runner import run_packet
        result = run_packet(theme)
        _active_tasks[task_id] = {
            "status": "completed",
            "result": result,
        }
    except Exception as e:
        _active_tasks[task_id] = {
            "status": "failed",
            "error": str(e),
        }
