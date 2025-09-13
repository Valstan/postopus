"""
Главный модуль веб-интерфейса Postopus.
"""
import os
import logging
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from .routers import auth, dashboard, posts, settings, scheduler
from .database import get_database
from .auth import get_current_user
from config import Config

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальная конфигурация
config = AppConfig.from_env()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Startup
    logger.info("Starting Postopus Web Interface...")
    await get_database().connect()
    yield
    # Shutdown
    logger.info("Shutting down Postopus Web Interface...")
    await get_database().close()

# Создаем приложение FastAPI
app = FastAPI(
    title="Postopus Web Interface",
    description="Веб-интерфейс для управления системой автоматической публикации контента",
    version="2.0.0",
    lifespan=lifespan
)

# Настраиваем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(scheduler.router, prefix="/api/scheduler", tags=["scheduler"])

# Статические файлы для фронтенда
app.mount("/static", StaticFiles(directory="web/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Главная страница."""
    with open("web/templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/health")
async def health_check():
    """Проверка здоровья приложения."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "database": "connected" if await get_database().is_connected() else "disconnected"
    }

@app.get("/api/info")
async def get_app_info():
    """Информация о приложении."""
    return {
        "name": "Postopus",
        "version": "2.0.0",
        "description": "Система автоматической публикации контента",
        "features": [
            "Автоматический парсинг контента",
            "Фильтрация и сортировка постов",
            "Публикация в социальных сетях",
            "Планировщик задач",
            "Веб-интерфейс управления"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
