#!/usr/bin/env python3
"""
Скрипт для подготовки проекта Postopus к развертыванию на Render.com
"""
import os
import sys
import subprocess
import json
from pathlib import Path

def print_step(step, description):
    """Выводит информацию о шаге."""
    print(f"\n🎯 Шаг {step}: {description}")
    print("=" * 50)

def run_command(command, description):
    """Выполняет команду и выводит результат."""
    print(f"📝 {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - успешно")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - ошибка: {e}")
        print(f"Вывод: {e.stdout}")
        print(f"Ошибка: {e.stderr}")
        return False

def check_git_status():
    """Проверяет статус Git репозитория."""
    print_step(1, "Проверка Git репозитория")
    
    # Проверяем, инициализирован ли Git
    if not Path(".git").exists():
        print("📝 Инициализируем Git репозиторий...")
        if not run_command("git init", "Инициализация Git"):
            return False
    
    # Проверяем статус
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        print("📝 Есть несохраненные изменения:")
        print(result.stdout)
        return True
    else:
        print("✅ Все изменения сохранены")
        return True

def create_env_file():
    """Создает .env файл для локальной разработки."""
    print_step(2, "Создание .env файла")
    
    if Path(".env").exists():
        print("✅ .env файл уже существует")
        return True
    
    if Path("env.example").exists():
        print("📝 Копируем env.example в .env...")
        if run_command("cp env.example .env", "Копирование .env файла"):
            print("⚠️  Не забудьте отредактировать .env файл с вашими настройками!")
            return True
    
    print("❌ Файл env.example не найден")
    return False

def check_required_files():
    """Проверяет наличие необходимых файлов."""
    print_step(3, "Проверка необходимых файлов")
    
    required_files = [
        "requirements_render.txt",
        "src/web/main_render.py",
        "render.yaml",
        "README.md",
        ".gitignore"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
        else:
            print(f"✅ {file}")
    
    if missing_files:
        print(f"❌ Отсутствуют файлы: {', '.join(missing_files)}")
        return False
    
    print("✅ Все необходимые файлы присутствуют")
    return True

def create_github_repo_instructions():
    """Создает инструкции для GitHub."""
    print_step(4, "Инструкции для GitHub")
    
    instructions = """
📋 ИНСТРУКЦИИ ДЛЯ СОЗДАНИЯ GITHUB РЕПОЗИТОРИЯ:

1. Перейдите на https://github.com
2. Нажмите "New repository"
3. Назовите репозиторий: postopus
4. Сделайте его публичным
5. НЕ добавляйте README, .gitignore или лицензию
6. Нажмите "Create repository"

📋 КОМАНДЫ ДЛЯ ЗАГРУЗКИ КОДА:

git add .
git commit -m "Initial commit: Postopus web platform"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/postopus.git
git push -u origin main

Замените YOUR_USERNAME на ваш GitHub username!
"""
    
    print(instructions)
    
    # Создаем файл с инструкциями
    with open("GITHUB_INSTRUCTIONS.txt", "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print("📝 Инструкции сохранены в GITHUB_INSTRUCTIONS.txt")

def create_render_instructions():
    """Создает инструкции для Render.com."""
    print_step(5, "Инструкции для Render.com")
    
    instructions = """
📋 ИНСТРУКЦИИ ДЛЯ RENDER.COM:

1. Перейдите на https://render.com
2. Войдите через GitHub
3. Создайте PostgreSQL базу данных:
   - Name: postopus-db
   - Plan: Free
4. Создайте Redis:
   - Name: postopus-redis
   - Plan: Free
5. Создайте Web Service:
   - Подключите GitHub репозиторий
   - Build Command: pip install -r requirements_render.txt
   - Start Command: python -m uvicorn src.web.main_render:app --host 0.0.0.0 --port $PORT
6. Создайте Background Worker (Celery):
   - Name: postopus-worker
   - Start Command: celery -A src.tasks.celery_app worker --loglevel=info
7. Создайте Background Worker (Scheduler):
   - Name: postopus-scheduler
   - Start Command: celery -A src.tasks.celery_app beat --loglevel=info

📋 ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ:

MONGO_CLIENT = (Connection String из PostgreSQL)
REDIS_URL = (Connection String из Redis)
CELERY_BROKER_URL = (Connection String из Redis)
CELERY_RESULT_BACKEND = (Connection String из Redis)
SECRET_KEY = (сгенерируйте случайную строку 32+ символов)
LOG_LEVEL = INFO
VK_TOKENS = your_vk_token_1,your_vk_token_2
VK_READ_TOKENS = your_read_token_1,your_read_token_2
VK_POST_TOKENS = your_post_token_1,your_post_token_2
VK_REPOST_TOKENS = your_repost_token_1,your_repost_token_2
TELEGRAM_BOT_TOKEN = your_bot_token
TELEGRAM_CHAT_ID = your_chat_id

📋 ПОСЛЕ РАЗВЕРТЫВАНИЯ:

1. Откройте URL вашего приложения
2. Зарегистрируйтесь как администратор
3. Настройте VK API токены
4. Создайте задачи в планировщике
5. Протестируйте работу

Подробная инструкция: DEPLOY_TO_RENDER.md
"""
    
    print(instructions)
    
    # Создаем файл с инструкциями
    with open("RENDER_INSTRUCTIONS.txt", "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print("📝 Инструкции сохранены в RENDER_INSTRUCTIONS.txt")

def generate_secret_key():
    """Генерирует секретный ключ."""
    import secrets
    return secrets.token_urlsafe(32)

def create_env_template():
    """Создает шаблон .env файла с примерными значениями."""
    print_step(6, "Создание шаблона .env файла")
    
    secret_key = generate_secret_key()
    
    env_template = f"""# Database configuration
MONGO_CLIENT=mongodb://localhost:27017/

# VK API tokens (comma-separated)
VK_TOKENS=your_vk_token_1,your_vk_token_2
VK_READ_TOKENS=your_read_token_1,your_read_token_2
VK_POST_TOKENS=your_post_token_1,your_post_token_2
VK_REPOST_TOKENS=your_repost_token_1,your_repost_token_2

# Telegram configuration
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Application settings
LOG_LEVEL=INFO
LOG_FILE=logs/postopus.log

# Security settings
SECRET_KEY={secret_key}
ENCRYPTION_KEY=your_encryption_key_here

# Render.com specific (will be set automatically)
# PORT=8000
# DATABASE_URL=postgresql://...
# REDIS_URL=redis://...
"""
    
    with open(".env.template", "w", encoding="utf-8") as f:
        f.write(env_template)
    
    print("✅ Создан .env.template с сгенерированным SECRET_KEY")
    print(f"🔑 Сгенерированный SECRET_KEY: {secret_key}")

def main():
    """Главная функция."""
    print("🚀 Подготовка Postopus к развертыванию на Render.com")
    print("=" * 60)
    
    # Проверяем, что мы в правильной директории
    if not Path("src").exists():
        print("❌ Запустите скрипт из корневой директории проекта Postopus")
        sys.exit(1)
    
    success = True
    
    # Выполняем все шаги
    success &= check_git_status()
    success &= create_env_file()
    success &= check_required_files()
    create_github_repo_instructions()
    create_render_instructions()
    create_env_template()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Подготовка завершена успешно!")
        print("\n📋 Следующие шаги:")
        print("1. Отредактируйте .env файл с вашими настройками")
        print("2. Следуйте инструкциям в GITHUB_INSTRUCTIONS.txt")
        print("3. Следуйте инструкциям в RENDER_INSTRUCTIONS.txt")
        print("4. Или используйте подробную инструкцию DEPLOY_TO_RENDER.md")
        print("\n🚀 Удачи с развертыванием!")
    else:
        print("❌ Подготовка завершена с ошибками")
        print("Проверьте сообщения выше и исправьте проблемы")
        sys.exit(1)

if __name__ == "__main__":
    main()
