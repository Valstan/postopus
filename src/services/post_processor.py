"""
Сервис для обработки постов.
"""
import logging
import sys
import os
from typing import List, Optional, Dict, Any
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.post import Post, Attachment
from utils.text_utils import TextProcessor
from utils.image_utils import ImageProcessor
from utils.date_utils import DateProcessor

logger = logging.getLogger(__name__)


class PostProcessor:
    """Основной класс для обработки постов."""
    
    def __init__(self):
        self.text_processor = TextProcessor()
        self.image_processor = ImageProcessor()
        self.date_processor = DateProcessor()
    
    def process_posts(self, posts: List[Dict[str, Any]], theme: str) -> List[Post]:
        """
        Обрабатывает список постов.
        
        Args:
            posts: Список сырых постов из VK API
            theme: Тема постов (novost, reklama, etc.)
            
        Returns:
            Список обработанных постов
        """
        processed_posts = []
        
        for post_data in posts:
            try:
                post = self._create_post_from_data(post_data)
                if self._should_process_post(post, theme):
                    processed_posts.append(post)
            except Exception as e:
                logger.error(f"Error processing post {post_data.get('id', 'unknown')}: {e}")
                continue
        
        # Сортируем по количеству просмотров
        processed_posts.sort(key=lambda x: x.views.get('count', 0) if x.views else 0, reverse=True)
        return processed_posts
    
    def _create_post_from_data(self, data: Dict[str, Any]) -> Post:
        """Создает объект Post из сырых данных VK API."""
        attachments = None
        if 'attachments' in data:
            attachments = self._create_attachments(data['attachments'])
        
        views = data.get('views')
        copy_history = data.get('copy_history')
        
        return Post(
            id=data['id'],
            owner_id=data['owner_id'],
            from_id=data['from_id'],
            text=data.get('text', ''),
            date=datetime.fromtimestamp(data['date']),
            views=views,
            attachments=attachments,
            copy_history=copy_history
        )
    
    def _create_attachments(self, attachments_data: List[Dict[str, Any]]) -> List[Attachment]:
        """Создает объекты Attachment из данных VK API."""
        attachments = []
        
        for att_data in attachments_data:
            att_type = att_data['type']
            
            if att_type == 'photo':
                # Для фото берем URL самого большого размера
                url = self._get_best_photo_url(att_data['photo']['sizes'])
                attachments.append(Attachment(
                    type=att_type,
                    owner_id=att_data['photo']['owner_id'],
                    id=att_data['photo']['id'],
                    url=url
                ))
            elif att_type in ['video', 'audio']:
                attachments.append(Attachment(
                    type=att_type,
                    owner_id=att_data[att_type]['owner_id'],
                    id=att_data[att_type]['id']
                ))
        
        return attachments
    
    def _get_best_photo_url(self, sizes: List[Dict[str, Any]]) -> str:
        """Возвращает URL фото лучшего качества."""
        if not sizes:
            return ""
        
        # Сортируем по размеру (ширина * высота)
        best_size = max(sizes, key=lambda x: x.get('width', 0) * x.get('height', 0))
        return best_size['url']
    
    def _should_process_post(self, post: Post, theme: str) -> bool:
        """
        Определяет, нужно ли обрабатывать пост.
        
        Args:
            post: Пост для проверки
            theme: Тема постов
            
        Returns:
            True если пост нужно обработать
        """
        # Проверка на возраст поста
        if not self.date_processor.is_post_fresh(post, theme):
            logger.debug(f"Post {post.get_unique_id()} is too old")
            return False
        
        # Проверка на дубликаты
        if self._is_duplicate(post, theme):
            logger.debug(f"Post {post.get_unique_id()} is duplicate")
            return False
        
        # Проверка на запрещенные группы/пользователи
        # TODO: Добавить проверку blacklist из базы данных
        # if abs(post.owner_id) in blacklist:
        #     logger.debug(f"Post {post.get_unique_id()} from blacklisted source")
        #     return False
        
        # Проверка текста на запрещенные слова
        if self.text_processor.contains_blacklisted_words(post.text):
            logger.debug(f"Post {post.get_unique_id()} contains blacklisted words")
            return False
        
        # Специфичные проверки для разных тем
        if not self._check_theme_specific_rules(post, theme):
            return False
        
        return True
    
    def _is_duplicate(self, post: Post, theme: str) -> bool:
        """Проверяет, является ли пост дубликатом."""
        post_id = post.get_unique_id()
        
        # TODO: Проверяем в базе данных
        # if post_id in database.get_processed_posts(theme):
        #     return True
        
        return False
    
    def _check_theme_specific_rules(self, post: Post, theme: str) -> bool:
        """Проверяет правила, специфичные для темы."""
        if theme == 'sosed':
            # Для "сосед" нужен хештег #Новости
            return '#Новости' in post.text
        
        elif theme in ['kino', 'music']:
            # Для кино и музыки нужны видео/аудио вложения
            return post.has_video_attachments() or any(att.type == 'audio' for att in post.attachments or [])
        
        elif theme == 'prikol':
            # Для приколов не берем длинные тексты
            return post.get_text_length() <= 100
        
        return True
