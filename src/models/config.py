"""
Модели конфигурации для Postopus.
"""
import os
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class VKConfig:
    """Конфигурация VK API."""
    app_id: str = ""
    client_secret: str = ""
    tokens: List[str] = field(default_factory=list)
    read_tokens: List[str] = field(default_factory=list)
    post_tokens: List[str] = field(default_factory=list)
    repost_tokens: List[str] = field(default_factory=list)


@dataclass
class TelegramConfig:
    """Конфигурация Telegram Bot."""
    bot_token: str = ""
    chat_id: str = ""


@dataclass
class DatabaseConfig:
    """Конфигурация базы данных."""
    mongo_client: str = "mongodb://localhost:27017/"
    database_name: str = "postopus"
    postgres_url: Optional[str] = None


@dataclass
class FilterConfig:
    """Конфигурация фильтров контента."""
    delete_msg_blacklist: List[str] = field(default_factory=list)
    clear_text_blacklist: Dict[str, Any] = field(default_factory=dict)
    black_id: List[int] = field(default_factory=list)
    bad_name_group: Dict[str, Any] = field(default_factory=dict)
    time_old_post: Dict[str, int] = field(default_factory=lambda: {
        "hard": 3600,    # 1 час
        "medium": 7200,  # 2 часа
        "light": 14400   # 4 часа
    })


@dataclass
class SecurityConfig:
    """Конфигурация безопасности."""
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


@dataclass
class AppConfig:
    """Главная конфигурация приложения."""
    vk: VKConfig = field(default_factory=VKConfig)
    telegram: TelegramConfig = field(default_factory=TelegramConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    filters: FilterConfig = field(default_factory=FilterConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    # Настройки приложения
    text_post_maxsize_simbols: int = 4000
    table_size: int = 30
    log_level: str = "INFO"
    
    # Заголовки и хештеги
    zagolovki: List[str] = field(default_factory=list)
    zagolovok: str = ""
    heshteg: str = ""
    heshteg_local: Dict[str, str] = field(default_factory=dict)
    
    # Рабочие данные (для совместимости с legacy кодом)
    work: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Создает конфигурацию из переменных окружения."""
        try:
            # VK конфигурация
            vk_tokens = os.getenv("VK_TOKENS", "").split(",") if os.getenv("VK_TOKENS") else []
            vk_read_tokens = os.getenv("VK_READ_TOKENS", "").split(",") if os.getenv("VK_READ_TOKENS") else []
            vk_post_tokens = os.getenv("VK_POST_TOKENS", "").split(",") if os.getenv("VK_POST_TOKENS") else []
            vk_repost_tokens = os.getenv("VK_REPOST_TOKENS", "").split(",") if os.getenv("VK_REPOST_TOKENS") else []
            
            vk_config = VKConfig(
                app_id=os.getenv("VK_APP_ID", ""),
                client_secret=os.getenv("VK_CLIENT_SECRET", ""),
                tokens=[token.strip() for token in vk_tokens if token.strip()],
                read_tokens=[token.strip() for token in vk_read_tokens if token.strip()],
                post_tokens=[token.strip() for token in vk_post_tokens if token.strip()],
                repost_tokens=[token.strip() for token in vk_repost_tokens if token.strip()]
            )
            
            # Telegram конфигурация
            telegram_config = TelegramConfig(
                bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
                chat_id=os.getenv("TELEGRAM_CHAT_ID", "")
            )
            
            # База данных
            database_config = DatabaseConfig(
                mongo_client=os.getenv("MONGO_CLIENT", "mongodb://localhost:27017/"),
                database_name=os.getenv("DATABASE_NAME", "postopus"),
                postgres_url=os.getenv("DATABASE_URL")
            )
            
            # Безопасность
            security_config = SecurityConfig(
                secret_key=os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production"),
                algorithm=os.getenv("ALGORITHM", "HS256"),
                access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
            )
            
            # Создаем основную конфигурацию
            config = cls(
                vk=vk_config,
                telegram=telegram_config,
                database=database_config,
                security=security_config,
                text_post_maxsize_simbols=int(os.getenv("TEXT_POST_MAXSIZE_SIMBOLS", "4000")),
                table_size=int(os.getenv("TABLE_SIZE", "30")),
                log_level=os.getenv("LOG_LEVEL", "INFO")
            )
            
            logger.info("Configuration loaded from environment variables")
            return config
            
        except Exception as e:
            logger.error(f"Error loading configuration from environment: {e}")
            return cls()  # Возвращаем конфигурацию по умолчанию
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует конфигурацию в словарь."""
        return {
            "vk": {
                "app_id": self.vk.app_id,
                "tokens_count": len(self.vk.tokens),
                "read_tokens_count": len(self.vk.read_tokens),
                "post_tokens_count": len(self.vk.post_tokens),
                "repost_tokens_count": len(self.vk.repost_tokens)
            },
            "telegram": {
                "bot_configured": bool(self.telegram.bot_token),
                "chat_configured": bool(self.telegram.chat_id)
            },
            "database": {
                "mongo_client": self.database.mongo_client,
                "database_name": self.database.database_name,
                "postgres_configured": bool(self.database.postgres_url)
            },
            "text_post_maxsize_simbols": self.text_post_maxsize_simbols,
            "table_size": self.table_size,
            "log_level": self.log_level
        }
    
    def get_vk_token(self, token_type: str = "main") -> Optional[str]:
        """Получает VK токен по типу."""
        if token_type == "read" and self.vk.read_tokens:
            return self.vk.read_tokens[0]
        elif token_type == "post" and self.vk.post_tokens:
            return self.vk.post_tokens[0]
        elif token_type == "repost" and self.vk.repost_tokens:
            return self.vk.repost_tokens[0]
        elif self.vk.tokens:
            return self.vk.tokens[0]
        return None
    
    def is_configured(self) -> bool:
        """Проверяет, настроена ли конфигурация."""
        return (
            bool(self.vk.tokens) and
            bool(self.database.mongo_client)
        )


# Для совместимости с legacy кодом
class Config:
    """Класс совместимости с legacy кодом."""
    
    def __init__(self):
        self._app_config = AppConfig.from_env()
    
    @property
    def MONGO_CLIENT(self) -> str:
        return self._app_config.database.mongo_client
    
    @property
    def VK_TOKENS(self) -> List[str]:
        return self._app_config.vk.tokens
    
    @property
    def TELEGRAM_BOT_TOKEN(self) -> str:
        return self._app_config.telegram.bot_token
    
    @property
    def TELEGRAM_CHAT_ID(self) -> str:
        return self._app_config.telegram.chat_id


# Глобальный экземпляр для legacy кода
config_instance = Config()