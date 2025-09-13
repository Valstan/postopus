"""
Модель поста для работы с контентом.
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class Attachment:
    """Вложение к посту."""
    type: str
    owner_id: int
    id: int
    url: Optional[str] = None


@dataclass
class Post:
    """Модель поста."""
    id: int
    owner_id: int
    from_id: int
    text: str
    date: datetime
    views: Optional[Dict[str, int]] = None
    attachments: Optional[List[Attachment]] = None
    copy_history: Optional[List[Dict[str, Any]]] = None
    
    @property
    def has_attachments(self) -> bool:
        """Проверяет наличие вложений."""
        return bool(self.attachments)
    
    @property
    def has_views(self) -> bool:
        """Проверяет наличие просмотров."""
        return bool(self.views and self.views.get('count', 0) > 0)
    
    @property
    def is_repost(self) -> bool:
        """Проверяет, является ли пост репостом."""
        return bool(self.copy_history)
    
    def get_unique_id(self) -> str:
        """Возвращает уникальный идентификатор поста."""
        return f"{abs(self.owner_id)}_{self.id}"
    
    def get_text_length(self) -> int:
        """Возвращает длину текста поста."""
        return len(self.text)
    
    def has_photo_attachments(self) -> bool:
        """Проверяет наличие фото вложений."""
        if not self.attachments:
            return False
        return any(att.type == 'photo' for att in self.attachments)
    
    def has_video_attachments(self) -> bool:
        """Проверяет наличие видео вложений."""
        if not self.attachments:
            return False
        return any(att.type == 'video' for att in self.attachments)
