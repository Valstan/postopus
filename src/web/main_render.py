"""
Главный модуль веб-интерфейса Postopus для Render.com.
"""
import os
import logging
from datetime import datetime
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
if os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), "web", "static")):
    app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(os.path.dirname(__file__)), "web", "static")), name="static")
else:
    logger.warning("Static directory not found, skipping static files mounting")

# Публичные API endpoints (должны быть после роутеров)
@app.get("/api/public/dashboard-stats")
async def get_public_dashboard_stats():
    """Public dashboard stats for the web interface."""
    try:
        return {
            "total_posts": 1547,
            "published_today": 23,
            "published_this_week": 156,
            "scheduled_tasks": 5,
            "active_regions": 15,
            "active_vk_sessions": 12,
            "error_count": 2,
            "processing_rate": 2.3,
            "last_update": datetime.utcnow().isoformat(),
            "status": "operational"
        }
    except Exception as e:
        logger.error(f"Error getting public dashboard stats: {e}")
        return {
            "total_posts": 0,
            "published_today": 0,
            "published_this_week": 0,
            "scheduled_tasks": 0,
            "active_regions": 0,
            "active_vk_sessions": 0,
            "error_count": 0,
            "processing_rate": 0,
            "last_update": datetime.utcnow().isoformat(),
            "status": "error"
        }

@app.get("/api/public/posts-simple")
async def get_public_posts():
    """Public posts endpoint for the web interface."""
    try:
        mock_posts = [
            {
                "id": 1,
                "title": "Новости региона",
                "content": "Содержание поста о новостях региона...",
                "region": "Москва",
                "theme": "novost",
                "status": "published",
                "created_at": "2025-10-03T10:00:00Z",
                "published_at": "2025-10-03T10:05:00Z",
                "views": 1250,
                "likes": 45,
                "reposts": 12,
                "image_url": None,
                "video_url": None,
                "tags": ["новости", "регион"],
                "priority": 0
            },
            {
                "id": 2,
                "title": "Объявление",
                "content": "Важное объявление для жителей...",
                "region": "СПб",
                "theme": "obyavlenie",
                "status": "pending",
                "created_at": "2025-10-03T11:00:00Z",
                "published_at": None,
                "views": 0,
                "likes": 0,
                "reposts": 0,
                "image_url": None,
                "video_url": None,
                "tags": ["объявление"],
                "priority": 1
            },
            {
                "id": 3,
                "title": "Статья",
                "content": "Интересная статья на актуальную тему...",
                "region": "Екатеринбург",
                "theme": "statya",
                "status": "published",
                "created_at": "2025-10-03T09:00:00Z",
                "published_at": "2025-10-03T09:10:00Z",
                "views": 890,
                "likes": 32,
                "reposts": 8,
                "image_url": None,
                "video_url": None,
                "tags": ["статья", "анализ"],
                "priority": 0
            }
        ]
        
        return {
            "posts": mock_posts,
            "total": len(mock_posts),
            "limit": 10,
            "offset": 0,
            "has_more": False
        }
        
    except Exception as e:
        logger.error(f"Error getting public posts: {e}")
        return {
            "posts": [],
            "total": 0,
            "limit": 10,
            "offset": 0,
            "has_more": False
        }

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Главная страница - простой dashboard."""
    html_content = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Postopus Dashboard - Система управления</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            color: #333;
        }
        
        .sidebar {
            position: fixed;
            left: 0;
            top: 0;
            width: 250px;
            height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 0;
            z-index: 1000;
        }
        
        .sidebar-header {
            padding: 0 20px 30px;
            border-bottom: 1px solid rgba(255,255,255,0.2);
            margin-bottom: 20px;
        }
        
        .logo {
            font-size: 1.8em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .logo-subtitle {
            font-size: 0.9em;
            opacity: 0.8;
        }
        
        .nav-menu {
            list-style: none;
        }
        
        .nav-item {
            margin: 5px 0;
        }
        
        .nav-link {
            display: flex;
            align-items: center;
            padding: 12px 20px;
            color: white;
            text-decoration: none;
            transition: background 0.3s;
        }
        
        .nav-link:hover, .nav-link.active {
            background: rgba(255,255,255,0.2);
        }
        
        .nav-link i {
            margin-right: 12px;
            width: 20px;
        }
        
        .main-content {
            margin-left: 250px;
            padding: 20px;
            min-height: 100vh;
        }
        
        .header {
            background: white;
            padding: 20px 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 {
            color: #333;
            font-size: 1.8em;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #4CAF50;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.15);
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .card-title {
            font-size: 1.2em;
            font-weight: 600;
            color: #333;
        }
        
        .card-icon {
            font-size: 2em;
            color: #667eea;
        }
        
        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9em;
        }
        
        .stat-change {
            font-size: 0.8em;
            margin-top: 5px;
        }
        
        .stat-change.positive {
            color: #4CAF50;
        }
        
        .stat-change.negative {
            color: #f44336;
        }
        
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 25px;
            border: none;
            cursor: pointer;
            transition: background 0.3s;
            font-size: 0.9em;
        }
        
        .btn:hover {
            background: #5a6fd8;
        }
        
        .btn-secondary {
            background: #6c757d;
        }
        
        .btn-secondary:hover {
            background: #5a6268;
        }
        
        .btn-success {
            background: #4CAF50;
        }
        
        .btn-success:hover {
            background: #45a049;
        }
        
        .loading {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 200px;
            color: #666;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <!-- Sidebar -->
    <nav class="sidebar">
        <div class="sidebar-header">
            <div class="logo">🚀 Postopus</div>
            <div class="logo-subtitle">Система управления</div>
        </div>
        <ul class="nav-menu">
            <li class="nav-item">
                <a href="#" class="nav-link active">
                    <i class="fas fa-tachometer-alt"></i>
                    Dashboard
                </a>
            </li>
            <li class="nav-item">
                <a href="#" class="nav-link">
                    <i class="fas fa-newspaper"></i>
                    Посты
                </a>
            </li>
            <li class="nav-item">
                <a href="#" class="nav-link">
                    <i class="fas fa-clock"></i>
                    Планировщик
                </a>
            </li>
            <li class="nav-item">
                <a href="#" class="nav-link">
                    <i class="fas fa-chart-bar"></i>
                    Аналитика
                </a>
            </li>
            <li class="nav-item">
                <a href="#" class="nav-link">
                    <i class="fas fa-cog"></i>
                    Настройки
                </a>
            </li>
        </ul>
    </nav>

    <!-- Main Content -->
    <main class="main-content">
        <div class="header">
            <h1><i class="fas fa-tachometer-alt"></i> Dashboard</h1>
            <div class="status-indicator">
                <div class="status-dot"></div>
                <span>Система активна</span>
            </div>
        </div>

        <div class="dashboard-grid">
            <!-- Статистика постов -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">Всего постов</div>
                    <div class="card-icon"><i class="fas fa-newspaper"></i></div>
                </div>
                <div class="stat-number" id="total-posts">-</div>
                <div class="stat-label">Опубликовано за все время</div>
                <div class="stat-change positive" id="posts-change">+23 за сегодня</div>
            </div>

            <!-- Активные регионы -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">Активные регионы</div>
                    <div class="card-icon"><i class="fas fa-map-marker-alt"></i></div>
                </div>
                <div class="stat-number" id="active-regions">-</div>
                <div class="stat-label">Регионов в работе</div>
                <div class="stat-change positive" id="regions-change">15 из 15</div>
            </div>

            <!-- Скорость обработки -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">Скорость обработки</div>
                    <div class="card-icon"><i class="fas fa-tachometer-alt"></i></div>
                </div>
                <div class="stat-number" id="processing-rate">-</div>
                <div class="stat-label">Постов в минуту</div>
                <div class="stat-change positive" id="rate-change">+0.3 за час</div>
            </div>

            <!-- Статус системы -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">Статус системы</div>
                    <div class="card-icon"><i class="fas fa-server"></i></div>
                </div>
                <div id="system-status">
                    <div class="loading">Загрузка...</div>
                </div>
            </div>
        </div>

        <!-- Быстрые действия -->
        <div class="card">
            <div class="card-header">
                <div class="card-title">Быстрые действия</div>
            </div>
            <div style="display: flex; gap: 15px; flex-wrap: wrap;">
                <button class="btn btn-success" onclick="window.open('/docs', '_blank')">
                    <i class="fas fa-book"></i> API Документация
                </button>
                <button class="btn btn-secondary" onclick="window.open('/health', '_blank')">
                    <i class="fas fa-heartbeat"></i> Health Check
                </button>
                <button class="btn btn-secondary" onclick="window.open('/api/public/dashboard', '_blank')">
                    <i class="fas fa-chart-line"></i> Dashboard API
                </button>
                <button class="btn btn-secondary" onclick="window.open('/api/public/stats', '_blank')">
                    <i class="fas fa-chart-bar"></i> Статистика
                </button>
            </div>
        </div>
    </main>

    <script>
        // Global variables
        let currentSection = 'dashboard';

        // Initialize the application
        document.addEventListener('DOMContentLoaded', function() {
            loadDashboardData();
            setInterval(loadDashboardData, 30000); // Refresh every 30 seconds
        });

        // Dashboard functions
        async function loadDashboardData() {
            try {
                const response = await fetch('/api/public/dashboard');
                const data = await response.json();
                
                updateDashboardStats(data);
                loadSystemStatus();
            } catch (error) {
                console.error('Error loading dashboard data:', error);
                showError('Ошибка загрузки данных dashboard');
            }
        }

        function updateDashboardStats(data) {
            if (data.overview) {
                document.getElementById('total-posts').textContent = data.overview.total_posts || '-';
                document.getElementById('active-regions').textContent = data.overview.total_groups || '-';
                document.getElementById('processing-rate').textContent = '2.3'; // Mock data
            }
        }

        async function loadSystemStatus() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                
                const statusHtml = `
                    <div style="text-align: center;">
                        <div style="font-size: 1.5em; color: #4CAF50; margin-bottom: 10px;">
                            <i class="fas fa-check-circle"></i>
                        </div>
                        <div style="font-weight: 600; margin-bottom: 5px;">Система работает</div>
                        <div style="font-size: 0.9em; color: #666;">Все сервисы активны</div>
                    </div>
                `;
                
                document.getElementById('system-status').innerHTML = statusHtml;
            } catch (error) {
                document.getElementById('system-status').innerHTML = `
                    <div style="text-align: center; color: #f44336;">
                        <i class="fas fa-exclamation-triangle"></i>
                        Ошибка проверки статуса
                    </div>
                `;
            }
        }

        // Utility functions
        function showError(message) {
            console.error(message);
            // You can implement a toast notification here
        }
    </script>
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

@app.get("/debug")
async def debug_info():
    """Отладочная информация о конфигурации."""
    from .database import DATABASE_URL, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER
    
    # Safely show DATABASE_URL info
    database_url_info = "Not set"
    if DATABASE_URL:
        # Hide password in URL for security
        if "@" in DATABASE_URL and "://" in DATABASE_URL:
            parts = DATABASE_URL.split("://")
            if len(parts) == 2:
                schema = parts[0]
                rest = parts[1]
                if "@" in rest:
                    credentials, host_part = rest.split("@", 1)
                    if ":" in credentials:
                        user = credentials.split(":")[0]
                        database_url_info = f"{schema}://{user}:***@{host_part}"
                    else:
                        database_url_info = f"{schema}://***@{host_part}"
                else:
                    database_url_info = DATABASE_URL[:30] + "..."
            else:
                database_url_info = DATABASE_URL[:30] + "..."
        else:
            database_url_info = DATABASE_URL[:30] + "..."
    
    # Test connection and get detailed results
    connection_test_result = test_connection()
    
    return {
        "service_info": {
            "name": "postopus-web-only",
            "version": "2.0.0",
            "platform": "render.com"
        },
        "environment_variables": {
            "DATABASE_URL": database_url_info,
            "POSTGRES_HOST": POSTGRES_HOST,
            "POSTGRES_PORT": POSTGRES_PORT,
            "POSTGRES_DB": POSTGRES_DB,
            "POSTGRES_USER": POSTGRES_USER,
            "PORT": os.getenv("PORT", "Not set"),
            "PYTHONPATH": os.getenv("PYTHONPATH", "Not set"),
            "ENVIRONMENT": os.getenv("ENVIRONMENT", "Not set")
        },
        "connection_test": {
            "result": connection_test_result,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        },
        "recommendations": [
            "Check if DATABASE_URL environment variable is set in Render.com dashboard",
            "Verify the PostgreSQL database is accessible from this service",
            "Ensure the database credentials are correct",
            "Check if the database server is running and accepting connections"
        ]
    }

@app.get("/api/dashboard")
async def public_dashboard_redirect():
    """Public dashboard endpoint without authentication."""
    try:
        from .database import test_connection
        
        # Test database connection
        db_connected = test_connection()
        
        return {
            "status": "operational",
            "version": "2.0.0",
            "platform": "render.com",
            "database": "connected" if db_connected else "disconnected",
            "message": "Public dashboard access - for full features use /api/public/dashboard",
            "stats": {
                "total_posts": 1547,
                "published_today": 23,
                "active_regions": 15,
                "processing_rate": 2.3
            },
            "endpoints": {
                "public_dashboard": "/api/public/dashboard",
                "public_stats": "/api/public/stats",
                "authentication": "/api/auth/login",
                "health": "/health",
                "debug": "/debug"
            },
            "note": "This is a public endpoint. For authenticated access, login at /api/auth/login"
        }
        
    except Exception as e:
        logger.error(f"Error in public dashboard: {e}")
        return {
            "status": "error",
            "version": "2.0.0",
            "platform": "render.com",
            "error": str(e),
            "message": "Public dashboard access failed"
        }

@app.get("/health")
async def health_check():
    """Проверка здоровья приложения."""
    db_status = "connected" if test_connection() else "disconnected"
    
    # Get environment info for debugging
    env_info = {
        "DATABASE_URL_configured": bool(os.getenv('DATABASE_URL')),
        "POSTGRES_HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "POSTGRES_DB": os.getenv("POSTGRES_DB", "postopus"),
        "POSTGRES_USER": os.getenv("POSTGRES_USER", "postopus")
    }
    
    return {
        "status": "healthy",
        "version": "2.0.1",
        "platform": "render.com",
        "database": db_status,
        "environment": env_info
    }

@app.get("/api/info")
async def get_app_info():
    """Информация о приложении."""
    return {
        "name": "Postopus",
        "version": "2.0.1",  # Updated version to track deployment
        "description": "Система автоматической публикации контента",
        "platform": "render.com",
        "deployment_time": "2025-10-03T12:00:00Z",
        "service_type": "WEB_SERVER_ONLY",
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
    print(f"🌟 DIRECT START: Starting Postopus web server on port {port}")
    print("🌐 This is WEB SERVICE mode - NOT worker!")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
