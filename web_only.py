#!/usr/bin/env python3
"""
Основной файл запуска веб-приложения Postopus для Render.com
"""
import os
import sys

# Добавляем src в Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Запуск веб-приложения"""
    try:
        print("🔧 Starting Postopus Web-Only Service...")
        print(f"📁 Working directory: {os.getcwd()}")
        print(f"🐍 Python path: {sys.path}")
        print(f"🌐 Environment: {os.getenv('ENVIRONMENT', 'unknown')}")
        print(f"🗃️ DATABASE_URL configured: {'Yes' if os.getenv('DATABASE_URL') else 'No'}")
        
        # Force web server mode - prevent any confusion with Celery
        if 'celery' in ' '.join(sys.argv).lower():
            print("❌ ERROR: This script should not run Celery commands!")
            print("❌ This is a web-only service. Use python web_only.py")
            sys.exit(1)
        
        from src.web.main_render import app
        import uvicorn
        
        # Получаем порт из переменной окружения (Render.com использует PORT)
        port = int(os.environ.get("PORT", 8000))
        host = os.environ.get("HOST", "0.0.0.0")
        
        print(f"🚀 Starting Postopus Web Server on {host}:{port}")
        print(f"📡 Service type: WEB SERVER (not worker)")
        
        # Запускаем приложение
        uvicorn.run(
            app, 
            host=host, 
            port=port, 
            log_level="info",
            access_log=True,
            reload=False
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(f"📁 Current directory contents:")
        for item in os.listdir('.'):
            print(f"  - {item}")
        if os.path.exists('src'):
            print(f"📁 src directory contents:")
            for item in os.listdir('src'):
                print(f"  - src/{item}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()