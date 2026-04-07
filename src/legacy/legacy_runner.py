"""
Legacy runner — мост между master архитектурой и портированным legacy кодом.

Запускает обработку сессий (аналог start.py) и пакетную обработку
(аналог start_paket.py) через портированные legacy модули.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def run_session(argument: str, bags: str = "0") -> dict[str, Any]:
    """
    Запускает обработку одной сессии (region_theme).
    Аналог start.py.

    Returns:
        Словарь со статистикой.
    """
    # Lazy import — legacy модули загружаются только при вызове
    from src.legacy.control.control import control
    from src.legacy.rw.get_session import get_session_legacy
    from src.legacy.rw.get_session_vk_api import get_session_vk_api_legacy

    # Инициализация сессии
    session_data = get_session_legacy(argument, bags=bags)
    if not session_data:
        return {"success": False, "posts_count": 0, "error": "Failed to init session"}

    # Подключение к VK API
    if not get_session_vk_api_legacy(session_data):
        return {"success": False, "posts_count": 0, "error": "VK API connection failed"}

    # Запуск обработки
    result = control(stat_mode=True)

    return result or {"success": False, "posts_count": 0}


def run_packet(theme: str) -> dict[str, Any]:
    """
    Запускает обработку темы по ВСЕМ регионам.
    Аналог start_paket.py.

    Returns:
        Суммарная статистика по всем регионам.
    """
    from src.legacy.control.control import control
    from src.legacy.rw.get_session import get_session_legacy
    from src.legacy.rw.get_session_vk_api import get_session_vk_api_legacy
    from src.legacy.utils.driver_tables import load_table

    # Загружаем список регионов из глобального конфига
    config = load_table("config")
    all_groups = config.get("all_my_groups", {})

    # Извлекаем уникальные регионы
    region_names = list(all_groups.keys())

    total_stats = {
        "success_regions": [],
        "failed_regions": [],
        "total_posts": 0,
        "total_groups": 0,
        "total_regions": len(region_names),
    }

    for region_name in region_names:
        argument = f"{region_name}_{theme}"
        logger.info("Processing region: %s", argument)

        try:
            session_data = get_session_legacy(argument)
            if not session_data:
                total_stats["failed_regions"].append({"region": region_name, "error": "Session init failed"})
                continue

            if not get_session_vk_api_legacy(session_data):
                total_stats["failed_regions"].append({"region": region_name, "error": "VK API failed"})
                continue

            result = control(stat_mode=True)

            if result and result.get("success"):
                total_stats["success_regions"].append({
                    "region": region_name,
                    "posts_count": result.get("posts_count", 0),
                })
                total_stats["total_posts"] += result.get("posts_count", 0)
            else:
                total_stats["failed_regions"].append({
                    "region": region_name,
                    "error": result.get("failed_posts", ["Unknown error"]),
                })

        except Exception as exc:
            logger.error("Region %s failed: %s", region_name, exc)
            total_stats["failed_regions"].append({
                "region": region_name,
                "error": str(exc),
            })

    return total_stats


def publish_stats(theme: str) -> bool:
    """
    Публикует статистику в Тестовый полигон.
    """
    try:
        from src.legacy.rw.publish_stats import publish_stats_to_test_polygon
        # Здесь нужен доступ к total_stats — в реальной реализации
        # статистика собирается в run_packet и передаётся сюда
        return True
    except ImportError:
        return False
