"""
Postopus Web Interface - Production Ready
Supports both development and production environments.
"""
import os
import logging
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
import sys
from pathlib import Path

# Add paths for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import routers
from .routers import auth, dashboard, posts, settings
try:
    from .routers import scheduler
except ImportError:
    scheduler = None

# Import database and auth
from .database import get_database
from .auth import get_current_user

# Import configuration
try:
    from ..config.production import config as production_config
    PRODUCTION_MODE = True
except ImportError:
    production_config = None
    PRODUCTION_MODE = False

# Fallback configuration
try:
    from src.models.config import AppConfig
except ImportError:
    class AppConfig:
        @classmethod
        def from_env(cls):
            return cls()

# Configure logging based on environment
if PRODUCTION_MODE and production_config:
    log_level = getattr(logging, production_config.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

# Load configuration
if PRODUCTION_MODE and production_config:
    config = production_config
    logger.info(f"Running in {production_config.environment} mode")
else:
    try:
        config = AppConfig.from_env()
        logger.info("Running in development mode with fallback config")
    except Exception as e:
        logger.warning(f"Could not load configuration: {e}")
        config = AppConfig()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    # Startup
    logger.info("Starting Postopus Web Interface...")
    
    if PRODUCTION_MODE:
        logger.info("Production mode enabled")
    
    try:
        await get_database().connect()
        logger.info("Database connected successfully")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        logger.info("Continuing with demo data fallback")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Postopus Web Interface...")
    try:
        await get_database().close()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")

# Create FastAPI application
app = FastAPI(
    title="Postopus Web Interface",
    description="Production-ready web interface for automated content publishing system",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if not (PRODUCTION_MODE and production_config and not production_config.debug) else None,
    redoc_url="/redoc" if not (PRODUCTION_MODE and production_config and not production_config.debug) else None
)

# Configure CORS
if PRODUCTION_MODE and production_config:
    allowed_origins = production_config.allowed_origins_list
else:
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])

# Include scheduler router if available
if scheduler:
    app.include_router(scheduler.router, prefix="/api/scheduler", tags=["scheduler"])
else:
    logger.warning("Scheduler router not available")

# Static files and templates (only in development or when files exist)
try:
    if os.path.exists("web/static"):
        app.mount("/static", StaticFiles(directory="web/static"), name="static")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")

@app.get("/", response_class=JSONResponse)
async def read_root():
    """API root endpoint with system information."""
    return {
        "message": "Postopus API is running",
        "version": "2.0.0",
        "environment": "production" if PRODUCTION_MODE else "development",
        "api_docs": "/docs" if not (PRODUCTION_MODE and production_config and not production_config.debug) else "disabled",
        "endpoints": {
            "authentication": "/api/auth",
            "dashboard": "/api/dashboard",
            "posts": "/api/posts",
            "settings": "/api/settings",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Enhanced health check for production monitoring."""
    health_status = {
        "status": "healthy",
        "version": "2.0.0",
        "environment": "production" if PRODUCTION_MODE else "development",
        "timestamp": None,
        "components": {}
    }
    
    # Import datetime here to avoid circular imports
    from datetime import datetime
    health_status["timestamp"] = datetime.utcnow().isoformat()
    
    # Check database
    try:
        db_connected = await get_database().is_connected()
        health_status["components"]["database"] = "connected" if db_connected else "disconnected"
    except Exception as e:
        health_status["components"]["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check configuration
    try:
        if PRODUCTION_MODE and production_config:
            health_status["components"]["config"] = "production"
        else:
            health_status["components"]["config"] = "development"
    except Exception as e:
        health_status["components"]["config"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status

@app.get("/api/info")
async def get_app_info():
    """Enhanced application information."""
    info = {
        "name": "Postopus",
        "version": "2.0.0",
        "description": "Automated content publishing system for Russian regional groups",
        "environment": "production" if PRODUCTION_MODE else "development",
        "features": [
            "Automated content parsing and filtering",
            "Multi-regional VK group management",
            "PostgreSQL database integration",
            "Role-based user management",
            "RESTful API with 25+ endpoints",
            "Production-ready deployment"
        ],
        "supported_regions": [
            "mi", "nolinsk", "arbazh", "kirs", "slob", "verhosh", "bogord",
            "yaransk", "viatpol", "zuna", "darov", "kilmez", "lebazh", "omut", "san"
        ],
        "content_themes": ["novost", "sosed", "kino", "music", "prikol", "reklama"]
    }
    
    if PRODUCTION_MODE and production_config:
        info["config"] = {
            "regions": len(production_config.supported_regions_list),
            "themes": len(production_config.content_themes_list),
            "max_posts_per_hour": production_config.max_posts_per_hour
        }
    
    return info

# Production startup
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    if PRODUCTION_MODE:
        # Production configuration
        uvicorn.run(
            "src.web.main:app",
            host=host,
            port=port,
            workers=1,
            log_level="info",
            access_log=True
        )
    else:
        # Development configuration
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=True,
            log_level="debug"
        )
