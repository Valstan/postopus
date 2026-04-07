"""
Модуль расчёта популярности поста VK.

Использует взвешенную формулу engagement rate с нормализацией по охвату,
похожую на алгоритмы Hacker News / Reddit но адаптированную для VK.

Формула:
    weighted_engagement = likes + comments * 2 + reposts * 3
    score = weighted_engagement / sqrt(views + 1)

Почему так:
- likes = 1 (базовое действие)
- comments = 2x (пользователь потратил время написать)
- reposts = 3x (самое ценное — пользователь поделился с аудиторией)
- sqrt(views + 1) — нормализация по охвату:
  пост с 1000 views и 10 likes МЕНЕЕ популярен чем
  пост с 200 views и 10 likes (выше engagement rate)
  но пост с 10000 views и 100 likes БОЛЕЕ популярен
  чем пост с 50 views и 5 likes (абсолютный охват тоже важен)
"""

from math import sqrt


def get_post_popularity_score(post: dict) -> float:
    """
    Рассчитывает score популярности поста.

    Args:
        post: Словарь поста VK с полями views, likes, reposts, comments.
              Каждое — dict с ключом {"count": N} или None.

    Returns:
        float: Score популярности. Чем выше — тем популярнее пост.
               Посты сортируются по убыванию этого значения.
    """
    views = _safe_count(post.get("views"))
    likes = _safe_count(post.get("likes"))
    comments = _safe_count(post.get("comments"))
    reposts = _safe_count(post.get("reposts"))

    # Взвешенный engagement: разные действия имеют разный вес
    weighted_engagement = likes + comments * 2 + reposts * 3

    # Нормализация по охвату: sqrt предотвращает доминирование
    # постов с огромными views но низким engagement rate
    score = weighted_engagement / sqrt(views + 1)

    return score


def _safe_count(metric) -> int:
    """Безопасно извлекает count из метрики VK."""
    if isinstance(metric, dict):
        return metric.get("count", 0)
    if isinstance(metric, (int, float)):
        return int(metric)
    return 0
