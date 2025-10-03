"""
Production configuration for Postopus deployment on Render.com
"""
import os
from typing import Optional, List
from pydantic import BaseSettings, Field


class ProductionConfig(BaseSettings):
    """Production configuration with environment variable support."""
    
    # Application Settings
    app_name: str = Field(default="Postopus", env="APP_NAME")
    app_version: str = Field(default="2.0.0", env="APP_VERSION")
    environment: str = Field(default="production", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_secret_key: Optional[str] = Field(None, env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    postgres_db: str = Field(default="postopus", env="POSTGRES_DB")
    postgres_user: str = Field(default="postopus_user", env="POSTGRES_USER")
    postgres_password: str = Field(..., env="POSTGRES_PASSWORD")
    
    # Redis
    redis_url: str = Field(..., env="REDIS_URL")
    
    # VK API
    vk_api_version: str = Field(default="5.131", env="VK_API_VERSION")
    vk_app_id: Optional[str] = Field(None, env="VK_APP_ID")
    vk_client_secret: Optional[str] = Field(None, env="VK_CLIENT_SECRET")
    
    # Telegram
    telegram_bot_token: Optional[str] = Field(None, env="TELEGRAM_BOT_TOKEN")
    
    # Regional Configuration
    default_region: str = Field(default="mi", env="DEFAULT_REGION")
    supported_regions: str = Field(
        default="mi,nolinsk,arbazh,kirs,slob,verhosh,bogord,yaransk,viatpol,zuna,darov,kilmez,lebazh,omut,san",
        env="SUPPORTED_REGIONS"
    )
    
    # Content Processing
    max_posts_per_hour: int = Field(default=10, env="MAX_POSTS_PER_HOUR")
    auto_publish_delay: int = Field(default=300, env="AUTO_PUBLISH_DELAY")
    content_themes: str = Field(
        default="novost,sosed,kino,music,prikol,reklama",
        env="CONTENT_THEMES"
    )
    
    # Monitoring
    sentry_dsn: Optional[str] = Field(None, env="SENTRY_DSN")
    health_check_enabled: bool = Field(default=True, env="HEALTH_CHECK_ENABLED")
    
    # CORS
    allowed_origins: str = Field(default="*", env="ALLOWED_ORIGINS")
    allowed_methods: str = Field(default="GET,POST,PUT,DELETE,OPTIONS", env="ALLOWED_METHODS")
    allowed_headers: str = Field(default="*", env="ALLOWED_HEADERS")
    
    # File Upload
    max_upload_size: int = Field(default=10485760, env="MAX_UPLOAD_SIZE")  # 10MB
    upload_dir: str = Field(default="/tmp/uploads", env="UPLOAD_DIR")
    
    # Celery
    celery_broker_url: str = Field(..., env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(..., env="CELERY_RESULT_BACKEND")
    celery_task_serializer: str = Field(default="json", env="CELERY_TASK_SERIALIZER")
    celery_result_serializer: str = Field(default="json", env="CELERY_RESULT_SERIALIZER")
    
    @property
    def supported_regions_list(self) -> List[str]:
        """Get supported regions as a list."""
        return [region.strip() for region in self.supported_regions.split(",")]
    
    @property
    def content_themes_list(self) -> List[str]:
        """Get content themes as a list."""
        return [theme.strip() for theme in self.content_themes.split(",")]
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Get allowed origins as a list."""
        if self.allowed_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() in ["development", "dev"]
    
    def get_database_config(self) -> dict:
        """Get database configuration dictionary."""
        return {
            "url": self.database_url,
            "database": self.postgres_db,
            "user": self.postgres_user,
        }
    
    def get_redis_config(self) -> dict:
        """Get Redis configuration dictionary."""
        return {
            "url": self.redis_url,
        }
    
    def get_vk_config(self) -> dict:
        """Get VK API configuration dictionary."""
        return {
            "api_version": self.vk_api_version,
            "app_id": self.vk_app_id,
            "client_secret": self.vk_client_secret,
        }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global production config instance
def get_production_config() -> ProductionConfig:
    """Get production configuration instance."""
    try:
        return ProductionConfig()
    except Exception as e:
        # Fallback configuration for development/testing
        print(f"Warning: Could not load production config: {e}")
        print("Using fallback configuration for development...")
        
        # Set minimal required environment variables
        os.environ.setdefault("SECRET_KEY", "fallback-secret-key-for-development")
        os.environ.setdefault("DATABASE_URL", "postgresql://localhost/postopus")
        os.environ.setdefault("POSTGRES_PASSWORD", "password")
        os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
        os.environ.setdefault("CELERY_BROKER_URL", "redis://localhost:6379/0")
        os.environ.setdefault("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
        
        return ProductionConfig()


# Initialize config
config = get_production_config()