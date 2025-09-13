"""
Главный модуль приложения Postopus.
"""
import logging
import sys
import asyncio
from pathlib import Path
from typing import Optional

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent.parent))

from src.models.config import AppConfig
from src.services.post_processor import PostProcessor
from src.services.vk_service import VKService
from src.services.database_service import DatabaseService
from src.utils.logger import setup_logging

logger = logging.getLogger(__name__)


class PostopusApp:
    """Главный класс приложения."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.post_processor = PostProcessor(config)
        self.vk_service = VKService(config)
        self.database_service = DatabaseService(config)
        
        # Настраиваем логирование
        setup_logging()
    
    async def run(self, session_name: str, bags: str = "0") -> None:
        """
        Запускает приложение.
        
        Args:
            session_name: Имя сессии для запуска
            bags: Режим отладки
        """
        try:
            logger.info(f"Starting Postopus with session: {session_name}, bags: {bags}")
            
            # Загружаем конфигурацию из базы данных
            await self.database_service.load_config()
            
            # Определяем тип сессии и запускаем соответствующий процесс
            if session_name == "100":
                await self._run_automatic_mode()
            elif session_name == "1":
                await self._run_service_mode()
            else:
                await self._run_session_mode(session_name, bags)
                
        except Exception as e:
            logger.error(f"Error running Postopus: {e}")
            raise
    
    async def _run_automatic_mode(self) -> None:
        """Запускает автоматический режим."""
        logger.info("Running in automatic mode")
        # Здесь будет логика автоматического режима
        pass
    
    async def _run_service_mode(self) -> None:
        """Запускает сервисный режим."""
        logger.info("Running in service mode")
        # Здесь будет логика сервисного режима
        pass
    
    async def _run_session_mode(self, session_name: str, bags: str) -> None:
        """Запускает режим конкретной сессии."""
        logger.info(f"Running session mode: {session_name}")
        
        # Загружаем данные сессии
        await self.database_service.load_session_data(session_name)
        
        # Получаем посты из VK
        posts_data = await self.vk_service.get_posts(session_name)
        
        if not posts_data:
            logger.warning("No posts found")
            return
        
        # Обрабатываем посты
        processed_posts = self.post_processor.process_posts(posts_data, session_name)
        
        if not processed_posts:
            logger.warning("No posts passed processing")
            return
        
        # Публикуем посты
        await self.vk_service.publish_posts(processed_posts, session_name)
        
        # Сохраняем изменения в базу данных
        await self.database_service.save_session_data(session_name)


async def main():
    """Главная функция."""
    # Создаем конфигурацию
    config = AppConfig.from_env()
    
    # Создаем приложение
    app = PostopusApp(config)
    
    # Получаем аргументы командной строки
    if len(sys.argv) == 3:
        session_name = sys.argv[1]
        bags = sys.argv[2]
    elif len(sys.argv) == 2:
        session_name = sys.argv[1]
        bags = "0"
    else:
        # Интерактивный режим
        session_name = input("\nEnter session name: ")
        bags = input("Enter bags mode (0-5): ")
    
    # Запускаем приложение
    await app.run(session_name, bags)


if __name__ == "__main__":
    asyncio.run(main())
