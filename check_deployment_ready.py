#!/usr/bin/env python3
"""
Скрипт для проверки готовности проекта к развертыванию на Render.com
"""
import os
import sys
from pathlib import Path

def print_step(step, description, status="✅"):
    """Выводит информацию о шаге."""
    print(f"{status} Шаг {step}: {description}")

def check_file_exists(file_path, description):
    """Проверяет существование файла."""
    if Path(file_path).exists():
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - файл не найден")
        return False

def check_requirements():
    """Проверяет requirements файлы."""
    print("\n🔍 Проверка requirements файлов...")
    
    files = [
        ("requirements_render.txt", "Requirements для Render.com"),
        ("requirements_web.txt", "Requirements для веб-приложения")
    ]
    
    all_good = True
    for file_path, description in files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    return all_good

def check_web_app():
    """Проверяет веб-приложение."""
    print("\n🔍 Проверка веб-приложения...")
    
    files = [
        ("src/web/main_render.py", "Главный файл веб-приложения"),
        ("src/web/routers/auth.py", "Роутер аутентификации"),
        ("src/web/routers/dashboard.py", "Роутер дашборда"),
        ("src/web/routers/posts.py", "Роутер постов"),
        ("src/web/routers/scheduler.py", "Роутер планировщика"),
        ("src/web/routers/settings.py", "Роутер настроек"),
        ("src/web/database.py", "Модуль базы данных")
    ]
    
    all_good = True
    for file_path, description in files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    return all_good

def check_celery():
    """Проверяет Celery задачи."""
    print("\n🔍 Проверка Celery задач...")
    
    files = [
        ("src/tasks/celery_app.py", "Celery приложение"),
        ("src/tasks/post_tasks.py", "Задачи постов"),
        ("src/tasks/scheduler_tasks.py", "Задачи планировщика")
    ]
    
    all_good = True
    for file_path, description in files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    return all_good

def check_config():
    """Проверяет конфигурационные файлы."""
    print("\n🔍 Проверка конфигурационных файлов...")
    
    files = [
        ("render.yaml", "Конфигурация Render.com"),
        (".gitignore", "Git ignore файл"),
        ("env.example", "Пример переменных окружения"),
        ("README.md", "Документация проекта")
    ]
    
    all_good = True
    for file_path, description in files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    return all_good

def check_tensorflow_removed():
    """Проверяет, что TensorFlow удален."""
    print("\n🔍 Проверка удаления TensorFlow...")
    
    try:
        with open("requirements_render.txt", "r", encoding="utf-8") as f:
            content = f.read()
        
        if "tensorflow" in content and not content.count("# tensorflow"):
            print("❌ TensorFlow не удален из requirements_render.txt")
            return False
        else:
            print("✅ TensorFlow удален из requirements_render.txt")
        
        with open("requirements_web.txt", "r", encoding="utf-8") as f:
            content = f.read()
        
        if "tensorflow" in content and not content.count("# tensorflow"):
            print("❌ TensorFlow не удален из requirements_web.txt")
            return False
        else:
            print("✅ TensorFlow удален из requirements_web.txt")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка при проверке TensorFlow: {e}")
        return False

def check_git_status():
    """Проверяет статус Git."""
    print("\n🔍 Проверка Git статуса...")
    
    try:
        import subprocess
        result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
        
        if result.stdout.strip():
            print("⚠️  Есть несохраненные изменения:")
            print(result.stdout)
            return False
        else:
            print("✅ Все изменения сохранены в Git")
            return True
    except Exception as e:
        print(f"❌ Ошибка при проверке Git: {e}")
        return False

def main():
    """Главная функция."""
    print("🚀 Проверка готовности Postopus к развертыванию на Render.com")
    print("=" * 70)
    
    checks = [
        ("Requirements файлы", check_requirements),
        ("Веб-приложение", check_web_app),
        ("Celery задачи", check_celery),
        ("Конфигурационные файлы", check_config),
        ("Удаление TensorFlow", check_tensorflow_removed),
        ("Git статус", check_git_status)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}:")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 70)
    
    if all_passed:
        print("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! Проект готов к развертыванию!")
        print("\n📋 Следующие шаги:")
        print("1. Перейдите на https://render.com")
        print("2. Следуйте инструкции в RENDER_STEP_BY_STEP.md")
        print("3. Создайте PostgreSQL, Redis и Web Service")
        print("4. Наслаждайтесь автоматизацией! 🚀")
    else:
        print("❌ НЕКОТОРЫЕ ПРОВЕРКИ НЕ ПРОЙДЕНЫ!")
        print("Исправьте ошибки выше и запустите скрипт снова.")
        sys.exit(1)

if __name__ == "__main__":
    main()
