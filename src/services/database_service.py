"""
Сервис для работы с базой данных.
"""
import logging
from typing import Dict, Any, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

from ..config import Config

logger = logging.getLogger(__name__)


class DatabaseService:
    """Сервис для работы с базой данных."""
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.database = None
    
    async def connect(self) -> bool:
        """
        Подключается к базе данных.
        
        Returns:
            True если подключение успешно
        """
        try:
            self.client = MongoClient(Config.MONGO_CLIENT)
            self.database = self.client["postopus"]
            
            # Тестируем соединение
            self.client.admin.command('ping')
            logger.info("Connected to MongoDB")
            return True
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            return False
    
    async def load_config(self) -> None:
        """Загружает конфигурацию из базы данных."""
        try:
            if not self.database:
                await self.connect()
            
            collection = self.database['config']
            config_doc = collection.find_one({'title': 'config'})
            
            if config_doc:
                # Обновляем конфигурацию данными из базы
                self._update_config_from_db(config_doc)
                logger.info("Configuration loaded from database")
            else:
                logger.warning("No configuration found in database")
                
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
    
    async def load_session_data(self, session_name: str) -> None:
        """
        Загружает данные сессии из базы данных.
        
        Args:
            session_name: Имя сессии
        """
        try:
            if not self.database:
                await self.connect()
            
            # Загружаем данные сессии
            collection = self.database[session_name.split('_')[0]]  # mi, dran, test
            session_doc = collection.find_one({'title': session_name})
            
            if session_doc:
                self.config.work[session_name] = session_doc
                logger.info(f"Session data loaded for {session_name}")
            else:
                logger.warning(f"No session data found for {session_name}")
                
        except Exception as e:
            logger.error(f"Error loading session data: {e}")
    
    async def save_session_data(self, session_name: str) -> None:
        """
        Сохраняет данные сессии в базу данных.
        
        Args:
            session_name: Имя сессии
        """
        try:
            if not self.database:
                await self.connect()
            
            if session_name not in self.config.work:
                logger.warning(f"No work data to save for {session_name}")
                return
            
            collection = self.database[session_name.split('_')[0]]
            session_data = self.config.work[session_name]
            
            # Ограничиваем размеры списков
            self._limit_list_sizes(session_data)
            
            # Сохраняем данные
            collection.update_one(
                {'title': session_name},
                {'$set': session_data},
                upsert=True
            )
            
            logger.info(f"Session data saved for {session_name}")
            
        except Exception as e:
            logger.error(f"Error saving session data: {e}")
    
    def _update_config_from_db(self, config_doc: Dict[str, Any]) -> None:
        """Обновляет конфигурацию данными из базы данных."""
        try:
            # Обновляем настройки фильтров
            if 'delete_msg_blacklist' in config_doc:
                self.config.filters.delete_msg_blacklist = config_doc['delete_msg_blacklist']
            
            if 'clear_text_blacklist' in config_doc:
                self.config.filters.clear_text_blacklist = config_doc['clear_text_blacklist']
            
            if 'black_id' in config_doc:
                self.config.filters.black_id = config_doc['black_id']
            
            if 'bad_name_group' in config_doc:
                self.config.filters.bad_name_group = config_doc['bad_name_group']
            
            if 'time_old_post' in config_doc:
                self.config.filters.time_old_post = config_doc['time_old_post']
            
            # Обновляем другие настройки
            if 'text_post_maxsize_simbols' in config_doc:
                self.config.text_post_maxsize_simbols = config_doc['text_post_maxsize_simbols']
            
            if 'table_size' in config_doc:
                self.config.table_size = config_doc['table_size']
            
            if 'zagolovki' in config_doc:
                self.config.zagolovki = config_doc['zagolovki']
            
            if 'zagolovok' in config_doc:
                self.config.zagolovok = config_doc['zagolovok']
            
            if 'heshteg' in config_doc:
                self.config.heshteg = config_doc['heshteg']
            
            if 'heshteg_local' in config_doc:
                self.config.heshteg_local = config_doc['heshteg_local']
                
        except Exception as e:
            logger.error(f"Error updating config from database: {e}")
    
    def _limit_list_sizes(self, session_data: Dict[str, Any]) -> None:
        """Ограничивает размеры списков в данных сессии."""
        try:
            max_size = self.config.table_size
            
            for key, value in session_data.items():
                if isinstance(value, list) and key in ['lip', 'hash']:
                    # Ограничиваем размер списка
                    if len(value) > max_size:
                        session_data[key] = value[-max_size:]
                        
        except Exception as e:
            logger.error(f"Error limiting list sizes: {e}")
    
    async def close(self) -> None:
        """Закрывает соединение с базой данных."""
        try:
            if self.client:
                self.client.close()
                logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")
