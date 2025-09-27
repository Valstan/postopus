"""
Простой веб-интерфейс Postopus для демонстрации.
"""
import os
import logging
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent.parent))

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем приложение FastAPI
app = FastAPI(
    title="Postopus Web Interface",
    description="Веб-интерфейс для управления системой автоматической публикации контента",
    version="2.0.0"
)

# Настраиваем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Главная страница."""
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
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                padding: 30px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            }
            h1 {
                text-align: center;
                color: #ffffff;
                margin-bottom: 30px;
                font-size: 2.5em;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .status-card {
                background: rgba(255, 255, 255, 0.2);
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                border-left: 4px solid #4CAF50;
            }
            .api-links {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .api-card {
                background: rgba(255, 255, 255, 0.15);
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                transition: transform 0.3s ease;
            }
            .api-card:hover {
                transform: translateY(-5px);
                background: rgba(255, 255, 255, 0.25);
            }
            .api-card a {
                color: #FFD700;
                text-decoration: none;
                font-weight: bold;
                font-size: 1.1em;
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
                margin: 30px 0;
            }
            .feature {
                background: rgba(255, 255, 255, 0.1);
                padding: 15px;
                border-radius: 8px;
                text-align: center;
            }
            .emoji {
                font-size: 2em;
                display: block;
                margin-bottom: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Postopus</h1>
            <p style="text-align: center; font-size: 1.2em; margin-bottom: 30px;">
                Система автоматической публикации контента в социальных сетях
            </p>
            
            <div class="status-card">
                <h3>✅ Статус системы</h3>
                <p>• Веб-интерфейс: <strong>Активен</strong></p>
                <p>• API: <strong>Доступен</strong></p>
                <p>• Аутентификация: <strong>Демо-режим</strong></p>
                <p>• База данных: <strong>MongoDB (готов к подключению)</strong></p>
            </div>

            <div class="api-links">
                <div class="api-card">
                    <h3>📋 API Документация</h3>
                    <p>Интерактивная документация Swagger</p>
                    <a href="/docs" target="_blank">Открыть /docs</a>
                </div>
                
                <div class="api-card">
                    <h3>🔧 ReDoc</h3>
                    <p>Альтернативная документация API</p>
                    <a href="/redoc" target="_blank">Открыть /redoc</a>
                </div>
                
                <div class="api-card">
                    <h3>📊 Информация</h3>
                    <p>Информация о приложении</p>
                    <a href="/api/info" target="_blank">Открыть /api/info</a>
                </div>
                
                <div class="api-card">
                    <h3>🔐 Аутентификация</h3>
                    <p>Статус системы входа</p>
                    <a href="/api/auth/status" target="_blank">Открыть /api/auth/status</a>
                </div>
            </div>

            <h3>🎯 Возможности системы</h3>
            <div class="features">
                <div class="feature">
                    <span class="emoji">🤖</span>
                    <strong>Автоматизация</strong><br>
                    Автоматический парсинг и публикация контента
                </div>
                <div class="feature">
                    <span class="emoji">📱</span>
                    <strong>Мульти-платформа</strong><br>
                    VK, Telegram, OK и другие
                </div>
                <div class="feature">
                    <span class="emoji">⏰</span>
                    <strong>Планировщик</strong><br>
                    Настройка расписания публикаций
                </div>
                <div class="feature">
                    <span class="emoji">📊</span>
                    <strong>Аналитика</strong><br>
                    Статистика по 15 регионам
                </div>
                <div class="feature">
                    <span class="emoji">🔍</span>
                    <strong>Фильтрация</strong><br>
                    Умная фильтрация контента
                </div>
                <div class="feature">
                    <span class="emoji">🎨</span>
                    <strong>Веб-интерфейс</strong><br>
                    Современный интерфейс управления
                </div>
            </div>

            <div style="text-align: center; margin-top: 40px; padding: 20px; background: rgba(0,0,0,0.2); border-radius: 10px;">
                <h3>🚧 Статус разработки</h3>
                <p>✅ Базовая архитектура готова<br>
                ✅ API интерфейс функционирует<br>
                ✅ Система конфигурации настроена<br>
                🔄 Подключение к базе данных<br>
                🔄 Полная интеграция с VK API</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Проверка здоровья приложения."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "message": "Postopus web interface is running"
    }

@app.get("/api/info")
async def get_app_info():
    """Информация о приложении."""
    return {
        "name": "Postopus",
        "version": "2.0.0",
        "description": "Система автоматической публикации контента",
        "status": "development",
        "features": [
            "Автоматический парсинг контента",
            "Фильтрация и сортировка постов", 
            "Публикация в социальных сетях",
            "Планировщик задач",
            "Веб-интерфейс управления",
            "15 региональных групп",
            "Система аналитики"
        ],
        "endpoints": {
            "main": "/",
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "info": "/api/info"
        }
    }

# Подключаем роутеры
from .routers.auth import router as auth_router
from .routers.dashboard import router as dashboard_router

app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get port from environment variable (Render.com uses PORT)
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"🚀 Starting Postopus on {host}:{port}")
    uvicorn.run(app, host=host, port=port)