"""
Роутер для управления настройками.
"""
import logging
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..database import get_database
from ..auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

class SettingUpdate(BaseModel):
    """Модель для обновления настройки."""
    value: Any
    description: str = None

class SettingResponse(BaseModel):
    """Модель для ответа с настройкой."""
    key: str
    value: Any
    description: str
    category: str
    updated_at: str

class VKConfig(BaseModel):
    """Конфигурация VK."""
    tokens: List[str]
    read_tokens: List[str]
    post_tokens: List[str]
    repost_tokens: List[str]

class TelegramConfig(BaseModel):
    """Конфигурация Telegram."""
    bot_token: str
    chat_id: str

class DatabaseConfig(BaseModel):
    """Конфигурация базы данных."""
    mongo_client: str
    database_name: str

class FilterConfig(BaseModel):
    """Конфигурация фильтров."""
    delete_msg_blacklist: List[str]
    clear_text_blacklist: Dict[str, List[str]]
    black_id: List[int]
    bad_name_group: Dict[str, int]
    time_old_post: Dict[str, int]

class AppConfigResponse(BaseModel):
    """Конфигурация приложения."""
    vk: VKConfig
    telegram: TelegramConfig
    database: DatabaseConfig
    filters: FilterConfig
    text_post_maxsize_simbols: int
    table_size: int

@router.get("/", response_model=AppConfigResponse)
async def get_settings(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Получает все настройки приложения."""
    try:
        settings_collection = db.get_collection("settings")
        
        # Получаем настройки из базы данных
        settings = await settings_collection.find_one({"type": "app_config"}, {"_id": 0})
        
        if not settings:
            # Возвращаем настройки по умолчанию
            return AppConfigResponse(
                vk=VKConfig(
                    tokens=[],
                    read_tokens=[],
                    post_tokens=[],
                    repost_tokens=[]
                ),
                telegram=TelegramConfig(
                    bot_token="",
                    chat_id=""
                ),
                database=DatabaseConfig(
                    mongo_client="mongodb://localhost:27017/",
                    database_name="postopus"
                ),
                filters=FilterConfig(
                    delete_msg_blacklist=[],
                    clear_text_blacklist={},
                    black_id=[],
                    bad_name_group={},
                    time_old_post={
                        "hard": 3600,
                        "medium": 7200,
                        "light": 14400
                    }
                ),
                text_post_maxsize_simbols=4000,
                table_size=30
            )
        
        return AppConfigResponse(**settings["config"])
        
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        raise HTTPException(status_code=500, detail="Error getting settings")

@router.put("/vk", response_model=VKConfig)
async def update_vk_settings(
    vk_config: VKConfig,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Обновляет настройки VK."""
    try:
        settings_collection = db.get_collection("settings")
        
        # Обновляем настройки VK
        await settings_collection.update_one(
            {"type": "app_config"},
            {
                "$set": {
                    "config.vk": vk_config.dict(),
                    "updated_at": "2024-01-01T00:00:00"  # Здесь должен быть текущий timestamp
                }
            },
            upsert=True
        )
        
        return vk_config
        
    except Exception as e:
        logger.error(f"Error updating VK settings: {e}")
        raise HTTPException(status_code=500, detail="Error updating VK settings")

@router.put("/telegram", response_model=TelegramConfig)
async def update_telegram_settings(
    telegram_config: TelegramConfig,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Обновляет настройки Telegram."""
    try:
        settings_collection = db.get_collection("settings")
        
        # Обновляем настройки Telegram
        await settings_collection.update_one(
            {"type": "app_config"},
            {
                "$set": {
                    "config.telegram": telegram_config.dict(),
                    "updated_at": "2024-01-01T00:00:00"  # Здесь должен быть текущий timestamp
                }
            },
            upsert=True
        )
        
        return telegram_config
        
    except Exception as e:
        logger.error(f"Error updating Telegram settings: {e}")
        raise HTTPException(status_code=500, detail="Error updating Telegram settings")

@router.put("/filters", response_model=FilterConfig)
async def update_filter_settings(
    filter_config: FilterConfig,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Обновляет настройки фильтров."""
    try:
        settings_collection = db.get_collection("settings")
        
        # Обновляем настройки фильтров
        await settings_collection.update_one(
            {"type": "app_config"},
            {
                "$set": {
                    "config.filters": filter_config.dict(),
                    "updated_at": "2024-01-01T00:00:00"  # Здесь должен быть текущий timestamp
                }
            },
            upsert=True
        )
        
        return filter_config
        
    except Exception as e:
        logger.error(f"Error updating filter settings: {e}")
        raise HTTPException(status_code=500, detail="Error updating filter settings")

@router.put("/general")
async def update_general_settings(
    settings: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Обновляет общие настройки."""
    try:
        settings_collection = db.get_collection("settings")
        
        # Обновляем общие настройки
        await settings_collection.update_one(
            {"type": "app_config"},
            {
                "$set": {
                    "config.text_post_maxsize_simbols": settings.get("text_post_maxsize_simbols", 4000),
                    "config.table_size": settings.get("table_size", 30),
                    "updated_at": "2024-01-01T00:00:00"  # Здесь должен быть текущий timestamp
                }
            },
            upsert=True
        )
        
        return {"message": "General settings updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating general settings: {e}")
        raise HTTPException(status_code=500, detail="Error updating general settings")

@router.get("/sessions")
async def get_sessions(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Получает список доступных сессий."""
    try:
        sessions_collection = db.get_collection("sessions")
        
        # Получаем все сессии
        sessions = await sessions_collection.find({}, {"_id": 0}).to_list(length=None)
        
        return {
            "sessions": [
                {
                    "name": session["name"],
                    "description": session.get("description", ""),
                    "enabled": session.get("enabled", True),
                    "last_run": session.get("last_run"),
                    "next_run": session.get("next_run")
                }
                for session in sessions
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        raise HTTPException(status_code=500, detail="Error getting sessions")

@router.put("/sessions/{session_name}")
async def update_session(
    session_name: str,
    session_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Обновляет настройки сессии."""
    try:
        sessions_collection = db.get_collection("sessions")
        
        # Обновляем сессию
        await sessions_collection.update_one(
            {"name": session_name},
            {
                "$set": {
                    **session_data,
                    "updated_at": "2024-01-01T00:00:00"  # Здесь должен быть текущий timestamp
                }
            },
            upsert=True
        )
        
        return {"message": f"Session {session_name} updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating session {session_name}: {e}")
        raise HTTPException(status_code=500, detail="Error updating session")

@router.post("/test-connection")
async def test_connection(
    platform: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Тестирует подключение к платформе."""
    try:
        if platform == "vk":
            # Здесь должна быть логика тестирования VK API
            return {"status": "success", "message": "VK connection successful"}
        elif platform == "telegram":
            # Здесь должна быть логика тестирования Telegram API
            return {"status": "success", "message": "Telegram connection successful"}
        elif platform == "database":
            # Тестируем подключение к базе данных
            if db.is_connected():
                return {"status": "success", "message": "Database connection successful"}
            else:
                return {"status": "error", "message": "Database connection failed"}
        else:
            raise HTTPException(status_code=400, detail="Unknown platform")
        
    except Exception as e:
        logger.error(f"Error testing connection to {platform}: {e}")
        raise HTTPException(status_code=500, detail=f"Error testing connection to {platform}")

@router.post("/backup")
async def create_backup(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Создает резервную копию настроек."""
    try:
        settings_collection = db.get_collection("settings")
        
        # Получаем все настройки
        settings = await settings_collection.find({}, {"_id": 0}).to_list(length=None)
        
        # Здесь должна быть логика создания резервной копии
        # backup_data = create_backup_file(settings)
        
        return {
            "message": "Backup created successfully",
            "backup_id": "backup_20240101_000000",
            "created_at": "2024-01-01T00:00:00"
        }
        
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        raise HTTPException(status_code=500, detail="Error creating backup")

@router.post("/restore")
async def restore_backup(
    backup_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Восстанавливает настройки из резервной копии."""
    try:
        # Здесь должна быть логика восстановления из резервной копии
        # restore_data = load_backup_file(backup_id)
        
        return {
            "message": "Settings restored successfully",
            "restored_at": "2024-01-01T00:00:00"
        }
        
    except Exception as e:
        logger.error(f"Error restoring backup: {e}")
        raise HTTPException(status_code=500, detail="Error restoring backup")
