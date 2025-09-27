#!/usr/bin/env python3
"""
Clean web-only entry point for Postopus (no Celery dependencies).
This ensures the web application can start independently.
"""
import os
import sys
import uvicorn
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Postopus Web Interface",
    description="Web interface for Postopus content automation system",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Main page."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Postopus - Content Automation System</title>
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
                text-align: center;
            }
            h1 {
                font-size: 3em;
                margin-bottom: 20px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .status {
                background: rgba(76, 175, 80, 0.2);
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                border-left: 4px solid #4CAF50;
            }
            .api-links {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 30px 0;
            }
            .api-card {
                background: rgba(255, 255, 255, 0.15);
                padding: 15px;
                border-radius: 10px;
                transition: transform 0.3s ease;
            }
            .api-card:hover {
                transform: translateY(-2px);
                background: rgba(255, 255, 255, 0.25);
            }
            .api-card a {
                color: #FFD700;
                text-decoration: none;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Postopus</h1>
            <p style="font-size: 1.3em; margin-bottom: 30px;">
                Content Automation System for Social Media
            </p>
            
            <div class="status">
                <h3>✅ System Status</h3>
                <p><strong>Web Application:</strong> Running Successfully</p>
                <p><strong>API:</strong> Available</p>
                <p><strong>Environment:</strong> Production</p>
                <p><strong>Version:</strong> 2.0.0</p>
            </div>

            <div class="api-links">
                <div class="api-card">
                    <h3>📋 API Docs</h3>
                    <a href="/docs" target="_blank">Open Swagger UI</a>
                </div>
                
                <div class="api-card">
                    <h3>🔧 ReDoc</h3>
                    <a href="/redoc" target="_blank">Open ReDoc</a>
                </div>
                
                <div class="api-card">
                    <h3>📊 API Info</h3>
                    <a href="/api/info" target="_blank">System Info</a>
                </div>
                
                <div class="api-card">
                    <h3>💚 Health</h3>
                    <a href="/health" target="_blank">Health Check</a>
                </div>
            </div>

            <div style="margin-top: 40px; padding: 20px; background: rgba(0,0,0,0.2); border-radius: 10px;">
                <h3>🎯 Key Features</h3>
                <p>✅ Automated content parsing and publishing<br>
                ✅ Multi-platform support (VK, Telegram, OK)<br>
                ✅ Regional content management (15 regions)<br>
                ✅ Task scheduling and analytics<br>
                ✅ Modern web interface</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "web",
        "version": "2.0.0",
        "environment": os.environ.get("ENVIRONMENT", "production")
    }

@app.get("/api/info")
async def get_app_info():
    """Application information."""
    return {
        "name": "Postopus",
        "version": "2.0.0",
        "description": "Content automation system for social media",
        "status": "production",
        "deployment": "render.com",
        "features": [
            "Automated content parsing",
            "Multi-platform publishing",
            "Regional content management",
            "Task scheduling",
            "Web interface",
            "Analytics dashboard"
        ]
    }

def main():
    """Main entry point."""
    try:
        # Get configuration from environment
        port = int(os.environ.get("PORT", 8000))
        host = os.environ.get("HOST", "0.0.0.0")
        environment = os.environ.get("ENVIRONMENT", "production")
        
        logger.info(f"🚀 Starting Postopus Web Application")
        logger.info(f"📍 Host: {host}:{port}")
        logger.info(f"🌍 Environment: {environment}")
        logger.info(f"📁 Working directory: {os.getcwd()}")
        
        # Start the server
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"❌ Error starting web application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()