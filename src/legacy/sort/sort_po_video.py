"""
Legacy сортировка: дедупликация видео по thumbnail histogram hash.

Портировано из old_postopus/bin/sort/sort_po_video.py.
Адаптировано: чистая функция, принимает hash_list и download_image.
"""

import hashlib
import logging
from typing import Any

logger = logging.getLogger(__name__)


def sort_po_video(
    msg: dict[str, Any],
    hash_list: list[str],
    download_image=None,
) -> bool:
    """
    Проверяет дубликаты видео по histogram hash превью.

    Args:
        msg: пост VK с attachments
        hash_list: список известных хешей
        download_image: функция скачивания фото по URL

    Returns:
        True если видео уже было (дубликат), False если новое
    """
    if "attachments" not in msg:
        return False

    for sample in msg["attachments"]:
        if sample.get("type") != "video":
            continue

        video = sample.get("video") or {}
        if video.get("title") == "Видео недоступно":
            continue

        # Берём превью видео
        url = None
        if "image" in video:
            url = video["image"]
        elif "photo_130" in video:
            url = video["photo_130"]
        elif "photo_320" in video:
            url = video["photo_320"]

        if not url or not download_image:
            continue

        try:
            from PIL import Image
            import io

            data = download_image(url)
            if not data:
                continue
            image = Image.open(io.BytesIO(data))
            histo = image.histogram()
            histo_hash = hashlib.md5(str(histo).encode()).hexdigest()

            if histo_hash in hash_list:
                return True  # Дубликат
            hash_list.append(histo_hash)

        except Exception as e:
            logger.warning("sort_po_video: ошибка обработки видео %s: %s", url, e)

    return False
