"""
Legacy сортировка: дедупликация фото по histogram hash.

Портировано из old_postopus/bin/sort/sort_po_foto.py.
Адаптировано: чистая функция, принимает hash_list и VK API.
НЕ использует PIL — использует metadata API VK для фото хеша.
"""

import hashlib
import logging
from typing import Any

logger = logging.getLogger(__name__)


def sort_po_foto(
    msg: dict[str, Any],
    hash_list: list[str],
    download_image=None,  # Optional callable для скачивания фото
) -> bool:
    """
    Проверяет дубликаты фото по histogram hash.

    Args:
        msg: пост VK с attachments
        hash_list: список уже известных хешей (session["work"][theme]["hash"])
        download_image: функция для скачивания фото по URL (опционально)
                       Если None — пропускает проверку

    Returns:
        True если фото уже было (дубликат), False если новое
    """
    if "attachments" not in msg or not msg["attachments"]:
        return False  # Нет вложений — не дубликат

    for sample in msg["attachments"]:
        if sample.get("type") != "photo":
            continue

        photo = sample.get("photo") or {}
        sizes = photo.get("sizes", [])

        # Берём фото нужного размера (200-650px)
        url = None
        for size in sizes:
            w = size.get("width", 0) or size.get("w", 0)
            if 200 <= w <= 650:
                url = size.get("url") or size.get("u")
                break

        if not url:
            continue

        if download_image:
            try:
                # Скачиваем и вычисляем hash
                histo = _compute_image_hash(url, download_image)
                if histo in hash_list:
                    return True  # Дубликат
                hash_list.append(histo)
            except Exception as e:
                logger.warning("sort_po_foto: ошибка обработки фото %s: %s", url, e)

    return False


def _compute_image_hash(url: str, download_image) -> str:
    """Вычисляет MD5 histogram hash для фото."""
    from PIL import Image
    import io

    data = download_image(url)
    if not data:
        return ""
    image = Image.open(io.BytesIO(data))
    histo = image.histogram()
    return hashlib.md5(str(histo).encode()).hexdigest()
