"""
Celery tasks для legacy модулей (портированных из old_postopus).

Заменяют cron-расписание и обеспечивают запуск обработки
регионов и тематик через Celery Beat.
"""

import logging
from typing import Any

from tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, time_limit=600)
def run_legacy_session_task(
    self,
    region_name: str,
    theme: str,
    bags: str = "0",
) -> dict[str, Any]:
    """
    Запускает обработку сессии для региона/темы (аналог start.py region_theme).

    Args:
        region_name: Название региона (например "Малмыж - Инфо")
        theme: Тематика (novost, kultura, sport и т.д.)
        bags: Режим фильтров (0-5)

    Returns:
        Словарь со статистикой обработки.
    """
    # Импортируем legacy модули только при вызове (ленивая загрузка)
    from src.legacy.legacy_runner import run_session

    try:
        logger.info("Starting legacy session: region=%s, theme=%s, bags=%s",
                     region_name, theme, bags)

        argument = f"{region_name}_{theme}"
        result = run_session(argument, bags=bags)

        logger.info("Legacy session completed: %s", argument)
        return result or {"success": False, "posts_count": 0}

    except Exception as exc:
        logger.error("Legacy session failed for %s_%s: %s",
                      region_name, theme, exc)
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, time_limit=1800)
def run_legacy_packet_task(
    self,
    theme: str,
) -> dict[str, Any]:
    """
    Запускает обработку темы по ВСЕМ регионам (аналог start_paket.py theme).

    Args:
        theme: Тематика (novost, kultura, sport и т.д.)

    Returns:
        Словарь с суммарной статистикой по всем регионам.
    """
    from src.legacy.legacy_runner import run_packet

    try:
        logger.info("Starting legacy packet: theme=%s", theme)
        result = run_packet(theme)
        logger.info("Legacy packet completed: theme=%s, regions=%d",
                     theme, result.get("total_regions", 0))
        return result

    except Exception as exc:
        logger.error("Legacy packet failed for theme=%s: %s", theme, exc)
        return {"success": False, "error": str(exc)}


@celery_app.task(time_limit=300)
def publish_legacy_stats_task(theme: str) -> bool:
    """
    Публикует статистику обработки в Тестовый полигон.

    Args:
        theme: Тематика (novost, kultura и т.д.)

    Returns:
        True если публикация успешна.
    """
    from src.legacy.legacy_runner import publish_stats

    try:
        logger.info("Publishing legacy stats for theme=%s", theme)
        return publish_stats(theme)
    except Exception as exc:
        logger.error("Failed to publish stats for %s: %s", theme, exc)
        return False
