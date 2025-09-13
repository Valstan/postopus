"""
Утилиты для работы с датами.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict

from ..models.post import Post

logger = logging.getLogger(__name__)


class DateProcessor:
    """Класс для обработки дат."""
    
    def __init__(self):
        # Временные ограничения по темам (в секундах)
        self.time_limits = {
            'hard': 3600,    # 1 час
            'medium': 7200,  # 2 часа
            'light': 14400   # 4 часа
        }
    
    def is_post_fresh(self, post: Post, theme: str) -> bool:
        """
        Проверяет, свежий ли пост.
        
        Args:
            post: Пост для проверки
            theme: Тема поста
            
        Returns:
            True если пост свежий
        """
        try:
            now = datetime.now()
            post_time = post.date
            difference = (now - post_time).total_seconds()
            
            # Определяем максимальный возраст поста в зависимости от темы
            max_age = self._get_max_age_for_theme(theme)
            
            return difference < max_age
        except Exception as e:
            logger.error(f"Error checking post freshness: {e}")
            return False
    
    def _get_max_age_for_theme(self, theme: str) -> int:
        """
        Возвращает максимальный возраст поста в секундах для темы.
        
        Args:
            theme: Тема поста
            
        Returns:
            Максимальный возраст в секундах
        """
        time_limits = self.time_limits
        
        # Жесткие ограничения для новостей и рекламы
        if theme in ['admin', 'novost', 'reklama', 'sosed', 'malmigrus']:
            return time_limits.get('hard', 3600)  # 1 час
        
        # Средние ограничения для детских садов, культуры и т.д.
        elif theme in ['detsad', 'kultura', 'union', 'sport', 'oblast_novost']:
            return time_limits.get('medium', 7200)  # 2 часа
        
        # Мягкие ограничения для развлекательного контента
        elif theme in ['krugozor', 'music', 'kino', 'prikol', 'art', 'repost_kultpodved']:
            return time_limits.get('light', 14400)  # 4 часа
        
        # По умолчанию - средние ограничения
        return time_limits.get('medium', 7200)
    
    def get_post_age_hours(self, post: Post) -> float:
        """
        Возвращает возраст поста в часах.
        
        Args:
            post: Пост для проверки
            
        Returns:
            Возраст в часах
        """
        try:
            now = datetime.now()
            post_time = post.date
            difference = now - post_time
            return difference.total_seconds() / 3600
        except Exception as e:
            logger.error(f"Error calculating post age: {e}")
            return 0.0
    
    def is_post_from_today(self, post: Post) -> bool:
        """
        Проверяет, опубликован ли пост сегодня.
        
        Args:
            post: Пост для проверки
            
        Returns:
            True если пост опубликован сегодня
        """
        try:
            now = datetime.now()
            post_date = post.date.date()
            today = now.date()
            return post_date == today
        except Exception as e:
            logger.error(f"Error checking if post is from today: {e}")
            return False
