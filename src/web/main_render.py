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

from .routers import auth, dashboard, posts, settings, scheduler, analytics, public
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
app.include_router(public.router, prefix="/api/public", tags=["public"])

# Static files for frontend (only if directory exists)
import os
if os.path.exists("web/static"):
    app.mount("/static", StaticFiles(directory="web/static"), name="static")
else:
    logger.warning("Static directory 'web/static' not found, skipping static files mounting")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Главная страница."""
    try:
        with open("web/templates/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        # Возвращаем встроенный HTML если файл не найден
        html_content = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Postopus - Система автоматической публикации</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 40px;
            max-width: 800px;
            text-align: center;
        }
        .logo {
            font-size: 3em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 20px;
        }
        .status {
            background: #4CAF50;
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            display: inline-block;
            margin: 20px 0;
        }
        .btn {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 12px 25px;
            text-decoration: none;
            border-radius: 25px;
            margin: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🚀 Postopus</div>
        <div class="status">✅ Система запущена и готова к работе</div>
        <p>Система автоматической публикации контента в социальные сети</p>
        <div>
            <a href="/docs" class="btn">📖 API Documentation</a>
            <a href="/health" class="btn">🔧 Health Check</a>
        </div>
        <p style="margin-top: 30px; color: #666; font-size: 0.9em;">
            Postopus v2.0.0 | Deployed on Render.com | PostgreSQL + Redis
        </p>
    </div>
</body>
</html>
        """
        return HTMLResponse(content=html_content)

@app.get("/test", response_class=HTMLResponse)
async def test_page():
    """Страница тестирования API."""
    try:
        with open("web/templates/test_api.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>API Test</title>
            <meta charset="utf-8">
        </head>
        <body>
            <h1>API Test Page</h1>
            <p>Страница тестирования API недоступна</p>
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
