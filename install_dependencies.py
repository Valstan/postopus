#!/usr/bin/env python3
"""
Скрипт для установки зависимостей для миграции.
"""
import subprocess
import sys

def install_package(package):
    """Установка пакета через pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} установлен успешно")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки {package}: {e}")
        return False

def main():
    """Установка всех необходимых зависимостей."""
    packages = [
        "pymongo",
        "sqlalchemy",
        "psycopg2-binary",
        "passlib"
    ]
    
    print("🔧 Устанавливаем зависимости для миграции...")
    print("=" * 50)
    
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Результат: {success_count}/{len(packages)} пакетов установлено")
    
    if success_count == len(packages):
        print("🎉 Все зависимости установлены! Можно запускать миграцию.")
    else:
        print("⚠️ Некоторые пакеты не удалось установить. Проверьте ошибки выше.")

if __name__ == "__main__":
    main()
