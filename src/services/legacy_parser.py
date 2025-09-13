"""
Улучшенная версия parser.py с новой архитектурой.
"""
import logging
import random
import sys
import os
from typing import List, Dict, Any, Optional

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.post import Post
from config import Config
from utils.text_utils import TextProcessor
from utils.date_utils import DateProcessor
from utils.image_utils import ImageProcessor
from .vk_service import VKService
from .database_service import DatabaseService

logger = logging.getLogger(__name__)


class LegacyParser:
    """
    Улучшенная версия парсера с новой архитектурой.
    Заменяет оригинальный parser.py.
    """
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.text_processor = TextProcessor(config)
        self.date_processor = DateProcessor(config)
        self.image_processor = ImageProcessor(config)
        self.vk_service = VKService(config)
        self.database_service = DatabaseService(config)
    
    async def parse_posts(self, session_name: str) -> List[Post]:
        """
        Основная функция парсинга постов.
        
        Args:
            session_name: Имя сессии
            
        Returns:
            Список обработанных постов
        """
        try:
            logger.info(f"Starting parsing for session: {session_name}")
            
            # Определяем тему
            theme = self._get_theme_for_session(session_name)
            
            # Получаем посты из VK
            posts_data = await self._get_posts_data(session_name, theme)
            if not posts_data:
                logger.warning("No posts data received")
                return []
            
            # Получаем старые посты для проверки дубликатов
            old_posts_data = await self._get_old_posts()
            
            # Обрабатываем посты
            processed_posts = await self._process_posts(posts_data, old_posts_data, theme)
            
            logger.info(f"Processed {len(processed_posts)} posts")
            return processed_posts
            
        except Exception as e:
            logger.error(f"Error parsing posts: {e}")
            return []
    
    def _get_theme_for_session(self, session_name: str) -> str:
        """Определяет тему по имени сессии."""
        if session_name in self.config.zagolovki:
            return 'novost'
        return session_name
    
    async def _get_posts_data(self, session_name: str, theme: str) -> List[Dict[str, Any]]:
        """Получает данные постов из VK."""
        try:
            if theme in ['novost', 'reklama']:
                # Для новостей и рекламы используем специальную логику
                return await self._get_news_posts(session_name)
            else:
                # Для других тем выбираем случайную группу
                group_id = self._get_random_group_for_theme(theme)
                if not group_id:
                    return []
                return await self.vk_service.get_posts_from_group(group_id, 20)
        except Exception as e:
            logger.error(f"Error getting posts data: {e}")
            return []
    
    async def _get_news_posts(self, session_name: str) -> List[Dict[str, Any]]:
        """Получает новостные посты."""
        try:
            # Получаем посты из группы новостей
            group_id = self.config.zagolovki.get(session_name)
            if not group_id:
                return []
            
            return await self.vk_service.get_posts_from_group(group_id, 20)
        except Exception as e:
            logger.error(f"Error getting news posts: {e}")
            return []
    
    async def _get_old_posts(self) -> List[Dict[str, Any]]:
        """Получает старые посты для проверки дубликатов."""
        try:
            # Получаем посты из группы публикации
            post_group_id = self._get_post_group_id()
            if not post_group_id:
                return []
            
            return await self.vk_service.get_posts_from_group(post_group_id, 100)
        except Exception as e:
            logger.error(f"Error getting old posts: {e}")
            return []
    
    def _get_random_group_for_theme(self, theme: str) -> Optional[int]:
        """Возвращает случайную группу для темы."""
        try:
            if theme in self.config.work and isinstance(self.config.work[theme], dict):
                groups = list(self.config.work[theme].values())
                if groups:
                    return random.choice(groups)
            return None
        except Exception as e:
            logger.error(f"Error getting random group: {e}")
            return None
    
    def _get_post_group_id(self) -> Optional[int]:
        """Возвращает ID группы для публикации."""
        # Здесь должна быть логика получения ID группы для публикации
        # Пока возвращаем заглушку
        return None
    
    async def _process_posts(
        self, 
        posts_data: List[Dict[str, Any]], 
        old_posts_data: List[Dict[str, Any]], 
        theme: str
    ) -> List[Post]:
        """Обрабатывает посты."""
        try:
            processed_posts = []
            
            # Создаем текст из старых постов для проверки дубликатов
            old_posts_text = self._create_old_posts_text(old_posts_data)
            
            for post_data in posts_data:
                try:
                    post = self._create_post_from_data(post_data)
                    
                    # Проверяем, нужно ли обрабатывать пост
                    if await self._should_process_post(post, theme, old_posts_text):
                        processed_posts.append(post)
                        
                        # Добавляем пост в список обработанных
                        self._add_post_to_processed(post, theme)
                        
                except Exception as e:
                    logger.error(f"Error processing post {post_data.get('id', 'unknown')}: {e}")
                    continue
            
            # Сортируем по количеству просмотров
            processed_posts.sort(
                key=lambda x: x.views.get('count', 0) if x.views else 0, 
                reverse=True
            )
            
            return processed_posts
            
        except Exception as e:
            logger.error(f"Error processing posts: {e}")
            return []
    
    def _create_old_posts_text(self, old_posts_data: List[Dict[str, Any]]) -> str:
        """Создает текст из старых постов для проверки дубликатов."""
        try:
            old_text = ""
            for post_data in old_posts_data:
                if 'text' in post_data and post_data['text']:
                    # Очищаем текст от копирования истории
                    text = self._clear_copy_history(post_data['text'])
                    if not self.text_processor.search_text([self.config.heshteg.get('reklama', '')], text):
                        old_text += self.text_processor.text_to_rafinad(text)
            return old_text
        except Exception as e:
            logger.error(f"Error creating old posts text: {e}")
            return ""
    
    def _clear_copy_history(self, text: str) -> str:
        """Очищает текст от копирования истории."""
        # Здесь должна быть логика очистки от копирования истории
        # Пока возвращаем исходный текст
        return text
    
    def _create_post_from_data(self, data: Dict[str, Any]) -> Post:
        """Создает объект Post из данных VK API."""
        try:
            from models.post import Post, Attachment
            from datetime import datetime
            
            # Создаем вложения
            attachments = None
            if 'attachments' in data:
                attachments = []
                for att_data in data['attachments']:
                    if att_data['type'] == 'photo':
                        url = self._get_best_photo_url(att_data['photo']['sizes'])
                        attachments.append(Attachment(
                            type=att_data['type'],
                            owner_id=att_data['photo']['owner_id'],
                            id=att_data['photo']['id'],
                            url=url
                        ))
                    elif att_data['type'] in ['video', 'audio']:
                        attachments.append(Attachment(
                            type=att_data['type'],
                            owner_id=att_data[att_data['type']]['owner_id'],
                            id=att_data[att_data['type']]['id']
                        ))
            
            return Post(
                id=data['id'],
                owner_id=data['owner_id'],
                from_id=data['from_id'],
                text=data.get('text', ''),
                date=datetime.fromtimestamp(data['date']),
                views=data.get('views'),
                attachments=attachments,
                copy_history=data.get('copy_history')
            )
        except Exception as e:
            logger.error(f"Error creating post from data: {e}")
            raise
    
    def _get_best_photo_url(self, sizes: List[Dict[str, Any]]) -> str:
        """Возвращает URL фото лучшего качества."""
        if not sizes:
            return ""
        
        try:
            # Выбираем размер с максимальной площадью
            best_size = max(sizes, key=lambda x: x.get('width', 0) * x.get('height', 0))
            return best_size.get('url', '')
        except Exception as e:
            logger.error(f"Error getting best photo URL: {e}")
            return ""
    
    async def _should_process_post(self, post: Post, theme: str, old_posts_text: str) -> bool:
        """Определяет, нужно ли обрабатывать пост."""
        try:
            # Проверка на возраст поста
            if not self.date_processor.is_post_fresh(post, theme):
                logger.debug(f"Post {post.get_unique_id()} is too old")
                return False
            
            # Проверка на дубликаты
            if self._is_duplicate(post, theme):
                logger.debug(f"Post {post.get_unique_id()} is duplicate")
                return False
            
            # Проверка на запрещенные группы/пользователи
            if abs(post.owner_id) in self.config.filters.black_id:
                logger.debug(f"Post {post.get_unique_id()} from blacklisted source")
                return False
            
            # Проверка текста на запрещенные слова
            if self.text_processor.contains_blacklisted_words(post.text):
                logger.debug(f"Post {post.get_unique_id()} contains blacklisted words")
                return False
            
            # Специфичные проверки для разных тем
            if not self._check_theme_specific_rules(post, theme):
                return False
            
            # Проверка на дубликаты по тексту
            if self._is_text_duplicate(post, old_posts_text):
                logger.debug(f"Post {post.get_unique_id()} is text duplicate")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking if post should be processed: {e}")
            return False
    
    def _is_duplicate(self, post: Post, theme: str) -> bool:
        """Проверяет, является ли пост дубликатом."""
        try:
            post_id = post.get_unique_id()
            
            # Проверяем в рабочей таблице
            if theme in self.config.work and 'lip' in self.config.work[theme]:
                if post_id in self.config.work[theme]['lip']:
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking duplicate: {e}")
            return False
    
    def _is_text_duplicate(self, post: Post, old_posts_text: str) -> bool:
        """Проверяет, является ли пост дубликатом по тексту."""
        try:
            if not old_posts_text:
                return False
            
            # Преобразуем текст поста в рафинад
            post_rafinad = self.text_processor.text_to_rafinad(post.text)
            
            # Проверяем, есть ли часть текста в старых постах
            text_part = post_rafinad[int(len(post_rafinad) * 0.2):int(len(post_rafinad) * 0.7)]
            return self.text_processor.search_text([text_part], old_posts_text)
            
        except Exception as e:
            logger.error(f"Error checking text duplicate: {e}")
            return False
    
    def _check_theme_specific_rules(self, post: Post, theme: str) -> bool:
        """Проверяет правила, специфичные для темы."""
        try:
            if theme == 'sosed':
                # Для "сосед" нужен хештег #Новости
                return '#Новости' in post.text
            
            elif theme in ['kino', 'music']:
                # Для кино и музыки нужны видео/аудио вложения
                if not post.attachments:
                    return False
                return any(att.type in ['video', 'audio'] for att in post.attachments)
            
            elif theme == 'prikol':
                # Для приколов не берем длинные тексты
                return post.get_text_length() <= 100
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking theme specific rules: {e}")
            return False
    
    def _add_post_to_processed(self, post: Post, theme: str) -> None:
        """Добавляет пост в список обработанных."""
        try:
            if theme not in self.config.work:
                self.config.work[theme] = {'lip': [], 'hash': []}
            
            if 'lip' not in self.config.work[theme]:
                self.config.work[theme]['lip'] = []
            
            # Добавляем ID поста
            post_id = post.get_unique_id()
            if post_id not in self.config.work[theme]['lip']:
                self.config.work[theme]['lip'].append(post_id)
            
            # Добавляем хеш изображений
            if post.attachments:
                for att in post.attachments:
                    if att.type == 'photo' and att.url:
                        image_hash = self.image_processor.get_image_hash(att.url)
                        if image_hash:
                            if 'hash' not in self.config.work[theme]:
                                self.config.work[theme]['hash'] = []
                            if image_hash not in self.config.work[theme]['hash']:
                                self.config.work[theme]['hash'].append(image_hash)
            
        except Exception as e:
            logger.error(f"Error adding post to processed: {e}")
