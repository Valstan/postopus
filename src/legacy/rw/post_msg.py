"""
Legacy VK: публикация поста.

Портировано из old_postopus/bin/rw/post_msg.py.
Адаптировано: принимает vk_api явно вместо session.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def post_msg(
    vk_api,
    group_id: int,
    text_send: str,
    attachments: str = "",
    from_group: int = 1,
    copy_right: str = "",
) -> Optional[dict]:
    """
    Публикует пост ВКонтакте.

    Args:
        vk_api: VK API объект
        group_id: ID группы для публикации
        text_send: Текст поста
        attachments: Вложения (photoX_Y, videoX_Y и т.д.)
        from_group: 1 — от имени группы, 0 — от имени пользователя
        copy_right: Копирайт (ссылка на источник)

    Returns:
        {'post_id': ..., 'url': ..., 'owner_id': ...} или None при ошибке
    """
    try:
        response = vk_api.wall.post(
            owner_id=group_id,
            from_group=from_group,
            message=text_send,
            attachments=attachments,
            copyright=copy_right,
        )

        if response and "post_id" in response:
            post_id = response["post_id"]
            post_url = f"https://vk.com/wall{group_id}_{post_id}"
            return {"post_id": post_id, "url": post_url, "owner_id": group_id}

        return None

    except Exception as exc:
        logger.error("post_msg: ошибка публикации в группу %d: %s", group_id, exc)
        return None
