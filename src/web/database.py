"""
Модуль для работы с базой данных в веб-интерфейсе.
"""
import logging
from typing import Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from ..models.config import AppConfig

logger = logging.getLogger(__name__)

class WebDatabase:
    """Класс для работы с базой данных в веб-интерфейсе."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.client: Optional[MongoClient] = None
        self.database = None
        self._connected = False
    
    async def connect(self) -> bool:
        """Подключается к базе данных."""
        try:
            self.client = MongoClient(self.config.database.mongo_client)
            self.database = self.client[self.config.database.database_name]
            
            # Тестируем соединение
            self.client.admin.command('ping')
            self._connected = True
            logger.info("Connected to MongoDB")
            return True
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self._connected = False
            return False
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            self._connected = False
            return False
    
    async def close(self) -> None:
        """Закрывает соединение с базой данных."""
        try:
            if self.client:
                self.client.close()
                self._connected = False
                logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")
    
    def is_connected(self) -> bool:
        """Проверяет, подключено ли приложение к базе данных."""
        return self._connected
    
    def get_collection(self, name: str):
        """Возвращает коллекцию по имени."""
        if not self.database:
            raise Exception("Database not connected")
        return self.database[name]

# Глобальный экземпляр базы данных
_db_instance: Optional[WebDatabase] = None

def get_database() -> WebDatabase:
    """Возвращает экземпляр базы данных."""
    global _db_instance
    if _db_instance is None:
        from ..models.config import AppConfig
        config = AppConfig.from_env()
        _db_instance = WebDatabase(config)
    return _db_instance
