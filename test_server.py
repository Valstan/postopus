#!/usr/bin/env python3
"""
Тестовый скрипт для проверки веб-сервера.
"""
import uvicorn
from src.web.main_render import app

if __name__ == "__main__":
    print("🚀 Запуск тестового сервера Postopus...")
    print("📱 Откройте http://localhost:8000 в браузере")
    print("🛑 Для остановки нажмите Ctrl+C")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
