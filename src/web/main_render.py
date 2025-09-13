"""
Главный модуль веб-интерфейса Postopus для Render.com.
"""
import os
import logging
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from .routers import auth, dashboard, posts, settings, scheduler, analytics
from .database import get_database, init_db, test_connection
from .routers.auth import get_current_user

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Startup
    logger.info("Starting Postopus Web Interface on Render.com...")
    
    # Тестируем подключение к PostgreSQL
    if test_connection():
        logger.info("✅ PostgreSQL connected successfully")
        # Инициализируем базу данных (создаем таблицы)
        if init_db():
            logger.info("✅ Database tables created successfully")
        else:
            logger.error("❌ Failed to create database tables")
    else:
        logger.error("❌ Failed to connect to PostgreSQL")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Postopus Web Interface...")

# Создаем приложение FastAPI
app = FastAPI(
    title="Postopus Web Interface",
    description="Веб-интерфейс для управления системой автоматической публикации контента",
    version="2.0.0",
    lifespan=lifespan
)

# Настраиваем CORS для Render.com
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
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

# Статические файлы для фронтенда
app.mount("/static", StaticFiles(directory="web/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Главная страница."""
    try:
        with open("web/templates/enhanced_dashboard.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        try:
            with open("web/templates/index.html", "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        except FileNotFoundError:
            return HTMLResponse(content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Postopus</title>
                <meta charset="utf-8">
            </head>
            <body>
                <h1>Postopus Web Interface</h1>
                <p>Система автоматической публикации контента</p>
                <p>Веб-интерфейс загружается...</p>
            </body>
            </html>
            """)

@app.get("/health")
async def health_check():
    """Проверка здоровья приложения."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "platform": "render.com",
        "database": "connected" if test_connection() else "disconnected"
    }

@app.get("/api/info")
async def get_app_info():
    """Информация о приложении."""
    return {
        "name": "Postopus",
        "version": "2.0.0",
        "description": "Система автоматической публикации контента",
        "platform": "render.com",
        "features": [
            "Автоматический парсинг контента",
            "Фильтрация и сортировка постов",
            "Публикация в социальных сетях",
            "Планировщик задач",
            "Веб-интерфейс управления"
        ]
    }

# Для Render.com используем gunicorn
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
