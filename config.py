"""
Основной файл конфигурации для совместимости с legacy кодом.
"""
import os
import sys
from pathlib import Path

# Добавляем src в путь для импортов
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

try:
    from src.models.config import AppConfig, Config as ConfigClass
    
    # Создаем глобальную конфигурацию
    app_config = AppConfig.from_env()
    config_obj = ConfigClass()
    
    # Для совместимости с legacy кодом
    MONGO_CLIENT = app_config.database.mongo_client
    VK_TOKENS = app_config.vk.tokens
    TELEGRAM_BOT_TOKEN = app_config.telegram.bot_token
    TELEGRAM_CHAT_ID = app_config.telegram.chat_id
    
    # Глобальные переменные для legacy кода
    session = {}  # Будет заполняться при загрузке сессий
    work = app_config.work
    
    # Экспортируем основные объекты
    __all__ = [
        'app_config', 'config_obj', 'session', 'work',
        'MONGO_CLIENT', 'VK_TOKENS', 'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID'
    ]
    
except ImportError as e:
    # Fallback для случаев, когда новая структура еще не готова
    print(f"Warning: Could not import new config system: {e}")
    
    # Минимальная конфигурация из переменных окружения
    MONGO_CLIENT = os.getenv("MONGO_CLIENT", "mongodb://localhost:27017/")
    VK_TOKENS = os.getenv("VK_TOKENS", "").split(",") if os.getenv("VK_TOKENS") else []
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
    
    session = {}
    work = {}
    app_config = None
    config_obj = None