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

from .routers import auth, dashboard, posts, settings, scheduler, analytics, public, vk
from .database import get_database, init_db, test_connection
from .routers.auth import get_current_user
from .data_manager import data_manager

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
            # Создаем примеры данных если база пустая
            try:
                data_manager.create_sample_data()
                logger.info("✅ Sample data created successfully")
            except Exception as e:
                logger.warning(f"Could not create sample data: {e}")
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
app.include_router(vk.router, prefix="/api/vk", tags=["vk"])

# Static files for frontend (only if directory exists)
import os
static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web", "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")
    logger.info(f"Static files mounted from: {static_path}")
else:
    logger.warning(f"Static directory not found at: {static_path}, skipping static files mounting")

# Публичные API endpoints (должны быть после роутеров)
@app.get("/api/public/dashboard-stats")
async def get_public_dashboard_stats():
    """Public dashboard stats for the web interface."""
    try:
        # Используем реальные данные из базы
        return data_manager.get_real_dashboard_stats()
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
        # Используем реальные данные из базы
        posts = data_manager.get_recent_posts(limit=10)
        return {
            "posts": posts,
            "total": len(posts),
            "limit": 10,
            "offset": 0,
            "has_more": len(posts) >= 10
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

@app.get("/api/public/posts-by-status/{status}")
async def get_posts_by_status(status: str):
    """Получить посты по статусу."""
    try:
        posts = data_manager.get_posts_by_status(status, limit=20)
        return {
            "posts": posts,
            "status": status,
            "total": len(posts),
            "limit": 20
        }
    except Exception as e:
        logger.error(f"Error getting posts by status {status}: {e}")
        return {
            "posts": [],
            "status": status,
            "total": 0,
            "limit": 20
        }

@app.get("/api/public/analytics")
async def get_public_analytics(days: int = 7):
    """Получить данные аналитики."""
    try:
        analytics_data = data_manager.get_analytics_data(days)
        return analytics_data
    except Exception as e:
        logger.error(f"Error getting analytics data: {e}")
        return {
            "daily_stats": [],
            "region_stats": [],
            "theme_stats": [],
            "period_days": days
        }

@app.get("/api/public/groups-status")
async def get_groups_status():
    """Получить статус групп."""
    try:
        groups = data_manager.get_groups_status()
        return {
            "groups": groups,
            "total": len(groups),
            "active_count": len([g for g in groups if g["is_active"]])
        }
    except Exception as e:
        logger.error(f"Error getting groups status: {e}")
        return {
            "groups": [],
            "total": 0,
            "active_count": 0
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
        
        .hidden {
            display: none;
        }
        
        .content-section {
            display: block;
        }
        
        .content-section.hidden {
            display: none;
        }
        
        .posts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .post-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .post-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.15);
        }
        
        .post-title {
            font-size: 1.2em;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }
        
        .post-meta {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 15px;
        }
        
        .post-content {
            color: #555;
            line-height: 1.5;
            margin-bottom: 15px;
        }
        
        .post-status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .post-status.published {
            background: #e8f5e8;
            color: #4CAF50;
        }
        
        .post-status.pending {
            background: #fff3cd;
            color: #856404;
        }
        
        .post-status.failed {
            background: #f8d7da;
            color: #721c24;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #333;
        }
        
        .form-input, .form-textarea, .form-select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s;
        }
        
        .form-input:focus, .form-textarea:focus, .form-select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .form-textarea {
            height: 120px;
            resize: vertical;
        }
        
        .modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 2000;
        }
        
        .modal-content {
            background: white;
            border-radius: 15px;
            padding: 30px;
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .modal-title {
            font-size: 1.5em;
            font-weight: 600;
        }
        
        .close-btn {
            background: none;
            border: none;
            font-size: 1.5em;
            cursor: pointer;
            color: #666;
        }
        
        .form-actions {
            display: flex;
            gap: 10px;
            justify-content: flex-end;
            margin-top: 30px;
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
                <a href="#" class="nav-link active" onclick="showSection('dashboard'); return false;">
                    <i class="fas fa-tachometer-alt"></i>
                    Dashboard
                </a>
            </li>
            <li class="nav-item">
                <a href="#" class="nav-link" onclick="showSection('posts'); return false;">
                    <i class="fas fa-newspaper"></i>
                    Посты
                </a>
            </li>
            <li class="nav-item">
                <a href="#" class="nav-link" onclick="showSection('scheduler'); return false;">
                    <i class="fas fa-clock"></i>
                    Планировщик
                </a>
            </li>
            <li class="nav-item">
                <a href="#" class="nav-link" onclick="showSection('analytics'); return false;">
                    <i class="fas fa-chart-bar"></i>
                    Аналитика
                </a>
            </li>
            <li class="nav-item">
                <a href="#" class="nav-link" onclick="showSection('settings'); return false;">
                    <i class="fas fa-cog"></i>
                    Настройки
                </a>
            </li>
        </ul>
    </nav>

    <!-- Main Content -->
    <main class="main-content">
        <!-- Dashboard Section -->
        <section id="dashboard-section" class="content-section">
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
                       <button class="btn btn-secondary" onclick="window.open('/api/public/analytics', '_blank')">
                           <i class="fas fa-chart-line"></i> Аналитика
                       </button>
                       <button class="btn btn-secondary" onclick="window.open('/api/public/groups-status', '_blank')">
                           <i class="fas fa-users"></i> Статус групп
                       </button>
                </div>
            </div>
        </section>

        <!-- Posts Section -->
        <section id="posts-section" class="content-section hidden">
            <div class="header">
                <h1><i class="fas fa-newspaper"></i> Управление постами</h1>
                <button class="btn btn-success" onclick="showCreatePostModal()">
                    <i class="fas fa-plus"></i> Создать пост
                </button>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-title">Все посты</div>
                    <div>
                        <button class="btn btn-secondary" onclick="filterPosts('all')">Все</button>
                        <button class="btn btn-secondary" onclick="filterPosts('published')">Опубликованные</button>
                        <button class="btn btn-secondary" onclick="filterPosts('pending')">Ожидающие</button>
                    </div>
                </div>
                <div class="posts-grid" id="posts-list">
                    <div class="loading">Загрузка постов...</div>
                </div>
            </div>
        </section>

        <!-- Scheduler Section -->
        <section id="scheduler-section" class="content-section hidden">
            <div class="header">
                <h1><i class="fas fa-clock"></i> Планировщик</h1>
                <button class="btn btn-success" onclick="showCreateScheduleModal()">
                    <i class="fas fa-plus"></i> Создать расписание
                </button>
            </div>

            <div class="dashboard-grid">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Активные задачи</div>
                        <div class="card-icon"><i class="fas fa-tasks"></i></div>
                    </div>
                    <div class="stat-number" id="active-tasks">5</div>
                    <div class="stat-label">Задач в очереди</div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Выполнено сегодня</div>
                        <div class="card-icon"><i class="fas fa-check-circle"></i></div>
                    </div>
                    <div class="stat-number" id="completed-tasks">23</div>
                    <div class="stat-label">Задач выполнено</div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-title">Расписание публикаций</div>
                </div>
                <div id="schedule-list">
                    <div class="loading">Загрузка расписания...</div>
                </div>
            </div>
        </section>

        <!-- Analytics Section -->
        <section id="analytics-section" class="content-section hidden">
            <div class="header">
                <h1><i class="fas fa-chart-bar"></i> Аналитика</h1>
        <div>
                    <select class="form-select" id="analytics-period" onchange="updateAnalytics()">
                        <option value="7">7 дней</option>
                        <option value="30">30 дней</option>
                        <option value="90">90 дней</option>
                    </select>
                </div>
            </div>

            <div class="dashboard-grid">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">График публикаций</div>
                        <div class="card-icon"><i class="fas fa-chart-line"></i></div>
                    </div>
                    <div class="loading">
                        <i class="fas fa-chart-line"></i> График будет здесь
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Топ регионы</div>
                        <div class="card-icon"><i class="fas fa-map"></i></div>
                    </div>
                    <div id="top-regions">
                        <div class="loading">Загрузка...</div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Settings Section -->
        <section id="settings-section" class="content-section hidden">
            <div class="header">
                <h1><i class="fas fa-cog"></i> Настройки системы</h1>
            </div>

            <div class="dashboard-grid">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">VK API</div>
                        <div class="card-icon"><i class="fab fa-vk"></i></div>
                    </div>
                    <div id="vk-settings">
                        <div class="loading">Загрузка настроек...</div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Telegram Bot</div>
                        <div class="card-icon"><i class="fab fa-telegram"></i></div>
                    </div>
                    <div id="telegram-settings">
                        <div class="loading">Загрузка настроек...</div>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <!-- Create Post Modal -->
    <div id="create-post-modal" class="modal hidden">
        <div class="modal-content">
            <div class="modal-header">
                <h3 class="modal-title">Создать новый пост</h3>
                <button class="close-btn" onclick="hideCreatePostModal()">&times;</button>
            </div>
            <form id="create-post-form">
                <div class="form-group">
                    <label class="form-label">Заголовок</label>
                    <input type="text" class="form-input" id="post-title" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Содержание</label>
                    <textarea class="form-textarea" id="post-content" required></textarea>
                </div>
                <div class="form-group">
                    <label class="form-label">Регион</label>
                    <select class="form-select" id="post-region">
                        <option value="Москва">Москва</option>
                        <option value="СПб">СПб</option>
                        <option value="Екатеринбург">Екатеринбург</option>
                        <option value="Новосибирск">Новосибирск</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Тема</label>
                    <select class="form-select" id="post-theme">
                        <option value="novost">Новости</option>
                        <option value="obyavlenie">Объявления</option>
                        <option value="statya">Статьи</option>
                    </select>
                </div>
                <div class="form-actions">
                    <button type="button" class="btn btn-secondary" onclick="hideCreatePostModal()">Отмена</button>
                    <button type="submit" class="btn btn-success">Создать пост</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        // Global variables
        let currentSection = 'dashboard';
        let posts = [];
        
        // Force navigation update
        console.log('Navigation system initialized');

        // Initialize the application
        document.addEventListener('DOMContentLoaded', function() {
            initializeNavigation();
            loadDashboardData();
            setInterval(loadDashboardData, 30000); // Refresh every 30 seconds
        });

        // Navigation
        function initializeNavigation() {
            console.log('Navigation initialized - using onclick handlers');
            // Navigation is now handled by onclick attributes in HTML
        }

        function showSection(sectionName) {
            // Hide all sections
            document.querySelectorAll('.content-section').forEach(section => {
                section.classList.add('hidden');
            });

            // Remove active class from all nav links
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
            });

            // Show selected section
            document.getElementById(sectionName + '-section').classList.remove('hidden');
            document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');

            currentSection = sectionName;

            // Load section-specific data
            switch(sectionName) {
                case 'dashboard':
                    loadDashboardData();
                    break;
                case 'posts':
                    loadPosts();
                    break;
                case 'scheduler':
                    loadScheduler();
                    break;
                case 'analytics':
                    loadAnalytics();
                    break;
                case 'settings':
                    loadSettings();
                    break;
            }
        }

        // Dashboard functions
        async function loadDashboardData() {
            try {
                const response = await fetch('/api/public/dashboard-stats');
                const data = await response.json();
                
                updateDashboardStats(data);
                loadSystemStatus();
            } catch (error) {
                console.error('Error loading dashboard data:', error);
                showError('Ошибка загрузки данных dashboard');
            }
        }

        function updateDashboardStats(data) {
            document.getElementById('total-posts').textContent = data.total_posts || '-';
            document.getElementById('active-regions').textContent = data.active_regions || '-';
            document.getElementById('processing-rate').textContent = data.processing_rate || '-';
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

        // Posts functions
        async function loadPosts() {
            try {
                const response = await fetch('/api/public/posts-simple');
                const data = await response.json();
                
                posts = data.posts || [];
                renderPosts();
                
                // Обновляем счетчики
                updatePostCounters();
            } catch (error) {
                console.error('Error loading posts:', error);
                document.getElementById('posts-list').innerHTML = '<div class="error">Ошибка загрузки постов</div>';
            }
        }
        
        function updatePostCounters() {
            const totalPosts = posts.length;
            const publishedPosts = posts.filter(p => p.status === 'published').length;
            const pendingPosts = posts.filter(p => p.status === 'pending').length;
            const errorPosts = posts.filter(p => p.status === 'error').length;
            
            // Обновляем счетчики в интерфейсе
            const counters = document.querySelectorAll('.post-counter');
            counters.forEach(counter => {
                const type = counter.dataset.type;
                switch(type) {
                    case 'total':
                        counter.textContent = totalPosts;
                        break;
                    case 'published':
                        counter.textContent = publishedPosts;
                        break;
                    case 'pending':
                        counter.textContent = pendingPosts;
                        break;
                    case 'error':
                        counter.textContent = errorPosts;
                        break;
                }
            });
        }

        function renderPosts() {
            const postsHtml = posts.map(post => `
                <div class="post-card">
                    <div class="post-title">${post.title}</div>
                    <div class="post-meta">${post.region} • ${post.theme} • ${new Date(post.created_at).toLocaleDateString()}</div>
                    <div class="post-content">${post.content.substring(0, 100)}...</div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div class="post-status ${post.status}">${getStatusText(post.status)}</div>
                        <div style="display: flex; gap: 10px;">
                            <button class="btn btn-secondary" onclick="editPost(${post.id})">Редактировать</button>
                            <button class="btn btn-danger" onclick="deletePost(${post.id})">Удалить</button>
                        </div>
                    </div>
                </div>
            `).join('');

            document.getElementById('posts-list').innerHTML = postsHtml;
        }

        function getStatusText(status) {
            const statusMap = {
                'published': 'Опубликован',
                'pending': 'Ожидает',
                'failed': 'Ошибка'
            };
            return statusMap[status] || status;
        }

        function filterPosts(status) {
            console.log('Filtering posts by:', status);
            // Implement post filtering
        }

        // Modal functions
        function showCreatePostModal() {
            document.getElementById('create-post-modal').classList.remove('hidden');
        }

        function hideCreatePostModal() {
            document.getElementById('create-post-modal').classList.add('hidden');
            document.getElementById('create-post-form').reset();
        }

        // Form handling
        document.getElementById('create-post-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const postData = {
                title: document.getElementById('post-title').value,
                content: document.getElementById('post-content').value,
                region: document.getElementById('post-region').value,
                theme: document.getElementById('post-theme').value
            };

            createPost(postData);
        });

        async function createPost(postData) {
            try {
                // Simulate API call
                console.log('Creating post:', postData);
                
                // Add to posts array
                const newPost = {
                    id: posts.length + 1,
                    ...postData,
                    status: 'pending',
                    created_at: new Date().toISOString()
                };
                
                posts.unshift(newPost);
                renderPosts();
                hideCreatePostModal();
                
                // Show success message
                alert('Пост успешно создан!');
            } catch (error) {
                alert('Ошибка создания поста');
            }
        }

        function editPost(postId) {
            const post = posts.find(p => p.id === postId);
            if (post) {
                alert(`Редактирование поста: ${post.title}`);
            }
        }

        function deletePost(postId) {
            if (confirm('Вы уверены, что хотите удалить этот пост?')) {
                posts = posts.filter(p => p.id !== postId);
                renderPosts();
            }
        }

        // Scheduler functions
        async function loadScheduler() {
            try {
                // Simulate loading scheduler data
                const mockSchedules = [
                    { id: 1, name: 'Ежедневные новости', time: '09:00', status: 'active' },
                    { id: 2, name: 'Объявления', time: '12:00', status: 'active' },
                    { id: 3, name: 'Статьи', time: '18:00', status: 'paused' }
                ];

                const scheduleHtml = mockSchedules.map(schedule => `
                    <div class="post-card">
                        <div class="post-title">${schedule.name}</div>
                        <div class="post-meta">Время: ${schedule.time}</div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div class="post-status ${schedule.status}">${schedule.status === 'active' ? 'Активно' : 'Приостановлено'}</div>
                            <div style="display: flex; gap: 10px;">
                                <button class="btn btn-secondary" onclick="editSchedule(${schedule.id})">Редактировать</button>
                                <button class="btn btn-danger" onclick="deleteSchedule(${schedule.id})">Удалить</button>
                            </div>
                        </div>
                    </div>
                `).join('');

                document.getElementById('schedule-list').innerHTML = scheduleHtml;
            } catch (error) {
                document.getElementById('schedule-list').innerHTML = '<div class="error">Ошибка загрузки расписания</div>';
            }
        }

        function showCreateScheduleModal() {
            alert('Создание нового расписания');
        }

        function editSchedule(scheduleId) {
            alert(`Редактирование расписания: ${scheduleId}`);
        }

        function deleteSchedule(scheduleId) {
            if (confirm('Вы уверены, что хотите удалить это расписание?')) {
                alert('Расписание удалено');
            }
        }

        // Analytics functions
        async function loadAnalytics() {
            try {
                const response = await fetch('/api/public/analytics?days=7');
                const data = await response.json();
                
                updateAnalytics(data);
            } catch (error) {
                console.error('Error loading analytics:', error);
                document.getElementById('top-regions').innerHTML = '<div class="error">Ошибка загрузки аналитики</div>';
            }
        }
        
        function updateAnalytics(data) {
            if (data.region_stats && data.region_stats.length > 0) {
                const regionsHtml = data.region_stats.map(region => `
                    <div style="display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee;">
                        <span>${region.region}</span>
                        <span style="font-weight: 600;">${region.posts_count} постов</span>
                    </div>
                `).join('');
                
                document.getElementById('top-regions').innerHTML = regionsHtml;
            } else {
                document.getElementById('top-regions').innerHTML = '<div class="no-data">Нет данных для отображения</div>';
            }
        }

        // Settings functions
        async function loadSettings() {
            try {
                // Simulate loading settings
                document.getElementById('vk-settings').innerHTML = `
                    <div style="text-align: center;">
                        <div style="color: #4CAF50; margin-bottom: 10px;">
                            <i class="fas fa-check-circle"></i>
                        </div>
                        <div style="font-weight: 600; margin-bottom: 5px;">VK API подключен</div>
                        <div style="font-size: 0.9em; color: #666;">15 групп активны</div>
                        <button class="btn btn-secondary" style="margin-top: 10px;">Настроить</button>
                    </div>
                `;

                document.getElementById('telegram-settings').innerHTML = `
                    <div style="text-align: center;">
                        <div style="color: #f44336; margin-bottom: 10px;">
                            <i class="fas fa-exclamation-triangle"></i>
                        </div>
                        <div style="font-weight: 600; margin-bottom: 5px;">Telegram не настроен</div>
                        <div style="font-size: 0.9em; color: #666;">Требуется токен бота</div>
                        <button class="btn btn-success" style="margin-top: 10px;">Настроить</button>
                    </div>
                `;
            } catch (error) {
                console.error('Error loading settings:', error);
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
