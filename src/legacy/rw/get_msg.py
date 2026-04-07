"""
Legacy VK API: получение постов из группы.

Адаптирован для master: использует ModernVKService или legacy session.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def get_msg(vk_api, group_id: int, offset: int = 0, count: int = 1) -> list:
    """
    Получает посты из группы VK.

    Args:
        vk_api: VK API объект (vk_session.get_api() или ModernVKService)
        group_id: ID группы VK (отрицательный для сообществ)
        offset: смещение
        count: количество постов

    Returns:
        Список постов или пустой список при ошибке.
    """
    try:
        result = vk_api.wall.get(owner_id=group_id, count=count, offset=offset)
        return result.get("items", [])
    except Exception as exc:
        error_msg = str(exc).lower()
        # Игнорируем ошибки доступа для закрытых групп
        if any(m in error_msg for m in [
            "invalid access_token",
            "user authorization failed",
            "access denied",
        ]):
            logger.debug("get_msg: access denied for group %d (normal for closed groups)", group_id)
        else:
            logger.warning("get_msg: error fetching from group %d: %s", group_id, exc)
        return []
