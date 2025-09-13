"""
Утилиты для работы с изображениями.
"""
import hashlib
import logging
from typing import List, Optional
from PIL import Image
import requests
from pathlib import Path

from ..models.config import AppConfig

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Класс для обработки изображений."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.temp_dir = Path("temp_images")
        self.temp_dir.mkdir(exist_ok=True)
    
    def get_image_hash(self, image_url: str) -> Optional[str]:
        """
        Получает хеш изображения для проверки дубликатов.
        
        Args:
            image_url: URL изображения
            
        Returns:
            MD5 хеш изображения или None при ошибке
        """
        try:
            # Скачиваем изображение
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Открываем изображение
            image = Image.open(io.BytesIO(response.content))
            
            # Получаем гистограмму
            histogram = image.histogram()
            
            # Создаем MD5 хеш
            hash_object = hashlib.md5(str(histogram).encode())
            return hash_object.hexdigest()
            
        except Exception as e:
            logger.error(f"Error getting image hash from {image_url}: {e}")
            return None
    
    def download_image(self, url: str, filename: str) -> bool:
        """
        Скачивает изображение по URL.
        
        Args:
            url: URL изображения
            filename: Имя файла для сохранения
            
        Returns:
            True если успешно скачано
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            file_path = self.temp_dir / filename
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            return True
        except Exception as e:
            logger.error(f"Error downloading image from {url}: {e}")
            return False
    
    def is_duplicate_image(self, image_url: str, theme: str) -> bool:
        """
        Проверяет, является ли изображение дубликатом.
        
        Args:
            image_url: URL изображения
            theme: Тема поста
            
        Returns:
            True если изображение уже было
        """
        try:
            image_hash = self.get_image_hash(image_url)
            if not image_hash:
                return False
            
            # Проверяем в рабочей таблице
            if 'work' in self.config and theme in self.config.work:
                if 'hash' in self.config.work[theme] and image_hash in self.config.work[theme]['hash']:
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking duplicate image: {e}")
            return False
    
    def add_image_hash(self, image_url: str, theme: str) -> None:
        """
        Добавляет хеш изображения в рабочую таблицу.
        
        Args:
            image_url: URL изображения
            theme: Тема поста
        """
        try:
            image_hash = self.get_image_hash(image_url)
            if not image_hash:
                return
            
            if 'work' not in self.config:
                self.config.work = {}
            if theme not in self.config.work:
                self.config.work[theme] = {'hash': []}
            if 'hash' not in self.config.work[theme]:
                self.config.work[theme]['hash'] = []
            
            self.config.work[theme]['hash'].append(image_hash)
            
        except Exception as e:
            logger.error(f"Error adding image hash: {e}")
    
    def get_best_image_url(self, sizes: List[dict], min_width: int = 200, max_width: int = 650) -> Optional[str]:
        """
        Выбирает лучший URL изображения из списка размеров.
        
        Args:
            sizes: Список размеров изображения
            min_width: Минимальная ширина
            max_width: Максимальная ширина
            
        Returns:
            URL лучшего изображения или None
        """
        if not sizes:
            return None
        
        try:
            # Фильтруем размеры по ширине
            suitable_sizes = [
                size for size in sizes
                if min_width <= size.get('width', 0) <= max_width
            ]
            
            if not suitable_sizes:
                # Если нет подходящих размеров, берем самый большой
                suitable_sizes = sizes
            
            # Выбираем размер с максимальной площадью
            best_size = max(suitable_sizes, key=lambda x: x.get('width', 0) * x.get('height', 0))
            return best_size.get('url')
            
        except Exception as e:
            logger.error(f"Error selecting best image URL: {e}")
            return None
    
    def cleanup_temp_files(self) -> None:
        """Очищает временные файлы."""
        try:
            for file_path in self.temp_dir.glob("*"):
                file_path.unlink()
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {e}")
