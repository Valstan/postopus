#!/usr/bin/env python3
"""
Скрипт проверки готовности проекта к развертыванию с PostgreSQL на Render.com
"""
import os
import sys
import subprocess
from pathlib import Path

def check_file_exists(file_path, description):
    """Проверяет существование файла"""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - НЕ НАЙДЕН")
        return False

def check_requirements_file(file_path, description):
    """Проверяет файл requirements"""
    if not Path(file_path).exists():
        print(f"❌ {description}: {file_path} - НЕ НАЙДЕН")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем наличие PostgreSQL зависимостей
    if 'psycopg2-binary' in content and 'sqlalchemy' in content:
        print(f"✅ {description}: PostgreSQL зависимости найдены")
        return True
    else:
        print(f"❌ {description}: PostgreSQL зависимости НЕ НАЙДЕНЫ")
        return False

def check_web_application():
    """Проверяет веб-приложение"""
    print("\n🔍 Проверка веб-приложения...")
    
    files_to_check = [
        ("src/web/main_render.py", "Главный файл приложения"),
        ("src/web/database.py", "Модуль базы данных"),
        ("src/web/models.py", "Модели SQLAlchemy"),
        ("src/web/routers/auth.py", "Роутер аутентификации"),
        ("src/web/routers/dashboard.py", "Роутер дашборда"),
        ("src/web/routers/posts.py", "Роутер постов"),
        ("src/web/routers/settings.py", "Роутер настроек"),
        ("src/web/routers/scheduler.py", "Роутер планировщика"),
    ]
    
    all_exist = True
    for file_path, description in files_to_check:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    return all_exist

def check_celery_tasks():
    """Проверяет Celery задачи"""
    print("\n🔍 Проверка Celery задач...")
    
    files_to_check = [
        ("src/tasks/celery_app.py", "Celery приложение"),
        ("src/tasks/post_tasks.py", "Задачи постов"),
        ("src/tasks/scheduler_tasks.py", "Задачи планировщика"),
    ]
    
    all_exist = True
    for file_path, description in files_to_check:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    return all_exist

def check_configuration_files():
    """Проверяет конфигурационные файлы"""
    print("\n🔍 Проверка конфигурационных файлов...")
    
    files_to_check = [
        ("render.yaml", "Render.com конфигурация"),
        ("env.example", "Пример переменных окружения"),
        ("requirements_render.txt", "Зависимости для Render.com"),
        ("Dockerfile.db", "Dockerfile для PostgreSQL"),
    ]
    
    all_exist = True
    for file_path, description in files_to_check:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    return all_exist

def check_postgresql_config():
    """Проверяет конфигурацию PostgreSQL"""
    print("\n🔍 Проверка конфигурации PostgreSQL...")
    
    # Проверяем env.example
    if Path("env.example").exists():
        with open("env.example", 'r', encoding='utf-8') as f:
            content = f.read()
        
        postgres_vars = ['POSTGRES_HOST', 'POSTGRES_PORT', 'POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD']
        all_vars_found = all(var in content for var in postgres_vars)
        
        if all_vars_found:
            print("✅ Переменные PostgreSQL найдены в env.example")
        else:
            print("❌ Переменные PostgreSQL НЕ НАЙДЕНЫ в env.example")
            return False
    else:
        print("❌ env.example не найден")
        return False
    
    # Проверяем render.yaml
    if Path("render.yaml").exists():
        with open("render.yaml", 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'mikrokredit-db' in content and 'POSTGRES_' in content:
            print("✅ Конфигурация PostgreSQL найдена в render.yaml")
        else:
            print("❌ Конфигурация PostgreSQL НЕ НАЙДЕНА в render.yaml")
            return False
    else:
        print("❌ render.yaml не найден")
        return False
    
    return True

def check_requirements():
    """Проверяет файлы requirements"""
    print("\n🔍 Проверка файлов requirements...")
    
    files_to_check = [
        ("requirements_render.txt", "Зависимости для Render.com"),
    ]
    
    all_good = True
    for file_path, description in files_to_check:
        if not check_requirements_file(file_path, description):
            all_good = False
    
    return all_good

def check_git_status():
    """Проверяет статус Git"""
    print("\n🔍 Проверка Git статуса...")
    
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            print("⚠️  Есть несохраненные изменения в Git")
            print("Рекомендуется сделать commit перед развертыванием")
            return False
        else:
            print("✅ Git репозиторий чистый")
            return True
    except subprocess.CalledProcessError:
        print("❌ Ошибка при проверке Git статуса")
        return False
    except FileNotFoundError:
        print("⚠️  Git не найден в системе")
        return False

def main():
    """Основная функция проверки"""
    print("🚀 Проверка готовности к развертыванию PostOpus с PostgreSQL на Render.com")
    print("=" * 70)
    
    checks = [
        ("Веб-приложение", check_web_application),
        ("Celery задачи", check_celery_tasks),
        ("Конфигурационные файлы", check_configuration_files),
        ("Конфигурация PostgreSQL", check_postgresql_config),
        ("Файлы requirements", check_requirements),
        ("Git статус", check_git_status),
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        if not check_func():
            all_passed = False
        print()
    
    print("=" * 70)
    
    if all_passed:
        print("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! Проект готов к развертыванию на Render.com")
        print("\n📋 Следующие шаги:")
        print("1. Создайте PostgreSQL базу данных на Render.com")
        print("2. Создайте Redis сервис на Render.com")
        print("3. Создайте Web Service на Render.com")
        print("4. Создайте Background Workers для Celery")
        print("5. Настройте переменные окружения")
        print("\n📖 Подробная инструкция: POSTGRESQL_DEPLOYMENT.md")
    else:
        print("❌ НЕКОТОРЫЕ ПРОВЕРКИ НЕ ПРОЙДЕНЫ!")
        print("Исправьте ошибки перед развертыванием")
        sys.exit(1)

if __name__ == "__main__":
    main()
