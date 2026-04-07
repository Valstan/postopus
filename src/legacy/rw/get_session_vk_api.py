"""
Legacy VK API: подключение через vk_api.

Портировано из old_postopus/bin/rw/get_session_vk_api.py.
Адаптировано: принимает токен явно, возвращает VkApi.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def get_session_vk_api(token: str):
    """
    Создаёт VK API сессию.

    Args:
        token: VK access token

    Returns:
        VkApi объект или None при ошибке
    """
    try:
        from vk_api import VkApi
        vk_session = VkApi(token=token)
        return vk_session.get_api()
    except Exception as e:
        logger.error("get_session_vk_api: ошибка подключения: %s", e)
        return None
