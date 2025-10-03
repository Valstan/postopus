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
        from src.web.main_render import app
        import uvicorn
        
        # Получаем порт из переменной окружения (Render.com использует PORT)
        port = int(os.environ.get("PORT", 8000))
        host = os.environ.get("HOST", "0.0.0.0")
        
        print(f"🚀 Запуск Postopus на {host}:{port}")
        print(f"📁 Рабочая директория: {os.getcwd()}")
        print(f"🐍 Python path: {sys.path}")
        
        # Запускаем приложение
        uvicorn.run(app, host=host, port=port, log_level="info")
        
    except Exception as e:
        print(f"❌ Ошибка запуска приложения: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()