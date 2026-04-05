from env_loader import logger, session


def sort_old_date(sample):
    """
    Проверяет что пост не старше заданного порога для текущей темы.
    
    Args:
        sample: пост из VK с полем date (timestamp)
        
    Returns:
        True если пост свежий, False если старый
    """
    try:
        difference = session["timestamp_now"] - sample["date"]
        
        # Определяем порог старости для текущей темы
        time_limits = session.get("time_old_post", {})
        
        if session["name_session"] in ("admin", "novost", "reklama", "sosed", "malmig"):
            threshold = time_limits.get("hard", 86400)  # По умолчанию 24 часа
        elif session["name_session"] in ("detsad", "kultura", "union", "sport", "oblast_novost"):
            threshold = time_limits.get("medium", 172800)  # По умолчанию 48 часов
        elif session["name_session"] in ("krugozor", "music", "kino", "prikol", "art", "repost_kultpodved"):
            threshold = time_limits.get("light", 604800)  # По умолчанию 7 дней
        else:
            logger.warning(f"Неизвестная тема '{session['name_session']}', используем порог medium")
            threshold = time_limits.get("medium", 172800)
        
        is_fresh = difference < threshold
        
        # Логируем для отладки ВСЕГДА (временно, для диагностики)
        difference_hours = difference / 3600
        threshold_hours = threshold / 3600
        logger.info(
            f"sort_old_date: тема={session.get('name_session', '?')}, "
            f"разница={difference_hours:.1f}ч ({difference} сек), "
            f"порог={threshold_hours:.1f}ч ({threshold} сек), "
            f"time_limits_from_db={time_limits}, "
            f"результ={'✅ СВЕЖИЙ' if is_fresh else '❌ СТАРЫЙ'}"
        )
        
        return is_fresh
        
    except KeyError as e:
        logger.error(f"sort_old_date: отсутствует ключ {e} в session для темы '{session.get('name_session')}'")
        # Возвращаем False (пост старый) чтобы избежать публикации очень старых постов
        return False
    except Exception as e:
        logger.error(f"sort_old_date: непредвиденная ошибка: {e}")
        return False
