"""
Legacy сортировка: фильтр постов по дате.

Портировано из old_postopus/bin/sort/sort_old_date.py.
Адаптировано: принимает theme и timestamp_now явно, не зависит от session.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Пороги старости по умолчанию (секунды)
TIME_THRESHOLDS = {
    "hard": 86400,       # 24 часа: novost, reklama, admin, sosed
    "medium": 172800,    # 48 часов: kultura, sport, detsad, union, oblast_novost
    "light": 604800,     # 7 дней: kino, music, krugozor, prikol, art
}

# Категории тем
THEME_HARD = {"admin", "novost", "reklama", "sosed", "malmig"}
THEME_MEDIUM = {"detsad", "kultura", "union", "sport", "oblast_novost"}
THEME_LIGHT = {"krugozor", "music", "kino", "prikol", "art", "repost_kultpodved"}


def sort_old_date(
    sample: dict[str, Any],
    theme: str,
    timestamp_now: int,
    time_limits: dict[str, int] | None = None,
) -> bool:
    """
    Проверяет что пост не старше заданного порога для темы.

    Args:
        sample: пост VK с полем date (timestamp)
        theme: тема (novost, kultura, sport и т.д.)
        timestamp_now: текущий Unix timestamp
        time_limits: кастомные пороги из БД (если None — используются дефолтные)

    Returns:
        True если пост свежий, False если старый
    """
    try:
        difference = timestamp_now - sample.get("date", 0)
        if difference < 0:
            # Пост из будущего — считаем свежим
            return True

        limits = time_limits or {}

        if theme in THEME_HARD:
            threshold = limits.get("hard", TIME_THRESHOLDS["hard"])
        elif theme in THEME_MEDIUM:
            threshold = limits.get("medium", TIME_THRESHOLDS["medium"])
        elif theme in THEME_LIGHT:
            threshold = limits.get("light", TIME_THRESHOLDS["light"])
        else:
            logger.warning("Неизвестная тема '%s', используем порог medium", theme)
            threshold = limits.get("medium", TIME_THRESHOLDS["medium"])

        is_fresh = difference < threshold

        if is_fresh:
            difference_hours = difference / 3600
            threshold_hours = threshold / 3600
            logger.debug(
                "✅ СВЕЖИЙ ПОСТ: тема=%s, возраст=%.1fч < порог=%.1fч | post_id=%s",
                theme, difference_hours, threshold_hours, sample.get("id"),
            )

        return is_fresh

    except Exception as e:
        logger.error("sort_old_date: ошибка для темы '%s': %s", theme, e)
        return False  # При ошибке считаем пост старым
