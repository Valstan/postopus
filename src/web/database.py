"""
Модуль для работы с базой данных PostgreSQL в веб-интерфейсе.
"""
import os
import logging
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

# Получение параметров подключения к PostgreSQL
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "postopus")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postopus")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postopus_password")

# Формирование URL подключения - приоритет DATABASE_URL для Render.com
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Создание движка SQLAlchemy
engine = create_engine(DATABASE_URL, echo=False)

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

class WebDatabase:
    """Класс для работы с базой данных PostgreSQL в веб-интерфейсе."""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        self._connected = False
    
    async def connect(self) -> bool:
        """Подключается к базе данных."""
        try:
            # Тестируем соединение
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                self._connected = True
                logger.info("Connected to PostgreSQL")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            self._connected = False
            return False
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            self._connected = False
            return False
    
    async def close(self) -> None:
        """Закрывает соединение с базой данных."""
        try:
            self.engine.dispose()
            self._connected = False
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")
    
    def is_connected(self) -> bool:
        """Проверяет, подключено ли приложение к базе данных."""
        return self._connected
    
    def get_session(self):
        """Возвращает сессию базы данных."""
        return self.SessionLocal()
    
    def init_db(self):
        """Инициализация базы данных - создание всех таблиц."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error creating database tables: {e}")
            return False

def get_db():
    """Получение сессии базы данных для FastAPI dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """Тестирование подключения к базе данных"""
    try:
        # Log connection details for debugging
        logger.info(f"Testing database connection...")
        logger.info(f"DATABASE_URL configured: {'Yes' if DATABASE_URL else 'No'}")
        logger.info(f"Host: {POSTGRES_HOST}")
        logger.info(f"Port: {POSTGRES_PORT}")
        logger.info(f"Database: {POSTGRES_DB}")
        logger.info(f"User: {POSTGRES_USER}")
        
        # Log partial connection string for debugging (without password)
        if DATABASE_URL:
            if "@" in DATABASE_URL:
                parts = DATABASE_URL.split("@")
                if len(parts) >= 2:
                    logger.info(f"Connection host: {parts[1]}")
            else:
                logger.info(f"DATABASE_URL format: {DATABASE_URL[:20]}...")
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info("✅ Подключение к PostgreSQL успешно!")
            return True
    except SQLAlchemyError as e:
        logger.error(f"❌ Ошибка подключения к PostgreSQL: {e}")
        logger.error(f"Connection string being used: {DATABASE_URL[:50] if DATABASE_URL else 'None'}...")
        return False
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка при подключении к БД: {e}")
        logger.error(f"Engine URL: {engine.url}")
        return False

def init_db():
    """Инициализация базы данных"""
    try:
        # Создание всех таблиц
        Base.metadata.create_all(bind=engine)
        logger.info("✅ База данных инициализирована успешно!")
        return True
    except SQLAlchemyError as e:
        logger.error(f"❌ Ошибка инициализации базы данных: {e}")
        return False

# Глобальный экземпляр базы данных
_db_instance: Optional[WebDatabase] = None

def get_database() -> WebDatabase:
    """Возвращает экземпляр базы данных."""
    global _db_instance
    if _db_instance is None:
        _db_instance = WebDatabase()
    return _db_instance