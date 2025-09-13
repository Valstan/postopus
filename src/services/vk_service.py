"""
Сервис для работы с VK API.
"""
import logging
import random
import asyncio
from typing import List, Dict, Any, Optional

from vk_api import VkApi
from vk_api.exceptions import VkApiError

from ..models.post import Post
from ..web.config import Config

logger = logging.getLogger(__name__)


class VKService:
    """Сервис для работы с VK API."""
    
    def __init__(self):
        self.vk_app: Optional[VkApi] = None
        self.current_token: Optional[str] = None
    
    async def get_posts(self, session_name: str, count: int = 20) -> List[Dict[str, Any]]:
        """
        Получает посты из VK.
        
        Args:
            session_name: Имя сессии
            count: Количество постов
            
        Returns:
            Список постов
        """
        try:
            # Выбираем токен для чтения
            token = self._get_read_token()
            if not token:
                logger.error("No valid read token available")
                return []
            
            # Создаем сессию VK
            if not await self._create_vk_session(token):
                return []
            
            # Определяем группу для чтения
            group_id = self._get_group_id_for_session(session_name)
            if not group_id:
                logger.error(f"No group ID found for session: {session_name}")
                return []
            
            # Получаем посты
            posts = await self._fetch_posts(group_id, count)
            logger.info(f"Fetched {len(posts)} posts from group {group_id}")
            
            return posts
            
        except Exception as e:
            logger.error(f"Error getting posts: {e}")
            return []
    
    async def publish_posts(self, posts: List[Post], session_name: str) -> None:
        """
        Публикует посты в VK.
        
        Args:
            posts: Список постов для публикации
            session_name: Имя сессии
        """
        try:
            # Выбираем токен для публикации
            token = self._get_post_token()
            if not token:
                logger.error("No valid post token available")
                return
            
            # Создаем сессию VK
            if not await self._create_vk_session(token):
                return
            
            # Определяем группу для публикации
            group_id = self._get_post_group_id()
            if not group_id:
                logger.error("No post group ID found")
                return
            
            # Публикуем посты
            for post in posts:
                await self._publish_single_post(post, group_id, session_name)
                # Небольшая задержка между публикациями
                await asyncio.sleep(random.uniform(1, 3))
            
            logger.info(f"Published {len(posts)} posts")
            
        except Exception as e:
            logger.error(f"Error publishing posts: {e}")
    
    def _get_read_token(self) -> Optional[str]:
        """Возвращает случайный токен для чтения."""
        tokens = Config.get_active_vk_tokens()
        if not tokens:
            return None
        return random.choice(tokens)
    
    def _get_post_token(self) -> Optional[str]:
        """Возвращает случайный токен для публикации."""
        tokens = Config.get_active_vk_tokens()
        if not tokens:
            return None
        return random.choice(tokens)
    
    async def _create_vk_session(self, token: str) -> bool:
        """
        Создает сессию VK API.
        
        Args:
            token: Токен VK
            
        Returns:
            True если сессия создана успешно
        """
        try:
            self.vk_app = VkApi(token=token)
            # Тестируем соединение
            self.vk_app.get_api().users.get()
            self.current_token = token
            return True
        except VkApiError as e:
            logger.error(f"VK API error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error creating VK session: {e}")
            return False
    
    def _get_group_id_for_session(self, session_name: str) -> Optional[int]:
        """Возвращает ID группы для сессии."""
        # Здесь должна быть логика определения группы по имени сессии
        # Пока возвращаем заглушку
        return None
    
    def _get_post_group_id(self) -> Optional[int]:
        """Возвращает ID группы для публикации."""
        # Здесь должна быть логика получения ID группы для публикации
        # Пока возвращаем заглушку
        return None
    
    async def _fetch_posts(self, group_id: int, count: int) -> List[Dict[str, Any]]:
        """
        Получает посты из группы.
        
        Args:
            group_id: ID группы
            count: Количество постов
            
        Returns:
            Список постов
        """
        try:
            if not self.vk_app:
                return []
            
            # Получаем посты из стены группы
            response = self.vk_app.get_api().wall.get(
                owner_id=group_id,
                count=count,
                offset=0
            )
            
            return response.get('items', [])
            
        except VkApiError as e:
            logger.error(f"VK API error fetching posts: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching posts: {e}")
            return []
    
    async def _publish_single_post(self, post: Post, group_id: int, session_name: str) -> None:
        """
        Публикует один пост.
        
        Args:
            post: Пост для публикации
            group_id: ID группы
            session_name: Имя сессии
        """
        try:
            if not self.vk_app:
                return
            
            # Формируем текст поста
            text = self._format_post_text(post, session_name)
            
            # Формируем вложения
            attachments = self._format_post_attachments(post)
            
            # Публикуем пост
            self.vk_app.get_api().wall.post(
                owner_id=group_id,
                message=text,
                attachments=attachments
            )
            
            logger.info(f"Published post {post.get_unique_id()}")
            
        except VkApiError as e:
            logger.error(f"VK API error publishing post: {e}")
        except Exception as e:
            logger.error(f"Error publishing post: {e}")
    
    def _format_post_text(self, post: Post, session_name: str) -> str:
        """Форматирует текст поста."""
        # Здесь должна быть логика форматирования текста
        # Пока возвращаем исходный текст
        return post.text
    
    def _format_post_attachments(self, post: Post) -> str:
        """Форматирует вложения поста."""
        if not post.attachments:
            return ""
        
        attachments = []
        for att in post.attachments:
            if att.type in ['photo', 'video', 'audio']:
                attachments.append(f"{att.type}{att.owner_id}_{att.id}")
        
        return ",".join(attachments)
