#!/usr/bin/env python3
"""
Скрипт инициализации базы данных PostgreSQL на Render.com
"""
import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    from src.web.models import Post, Group, Schedule, User, Base
    from src.web.database import DATABASE_URL
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Установите зависимости: pip install sqlalchemy psycopg2-binary")
    sys.exit(1)

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_database():
    """Инициализация базы данных."""
    logger.info("🗄️ Инициализируем базу данных PostgreSQL...")
    
    try:
        # Подключаемся к PostgreSQL
        engine = create_engine(DATABASE_URL, echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        
        # Тестируем соединение
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info("✅ Подключение к PostgreSQL успешно")
        
        # Создаем таблицы
        logger.info("🔄 Создаем таблицы...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Таблицы созданы успешно")
        
        # Создаем пользователя администратора
        logger.info("👤 Создаем пользователя администратора...")
        
        # Проверяем, есть ли уже пользователи
        existing_users = session.query(User).count()
        if existing_users == 0:
            admin_user = User(
                username="admin",
                email="admin@postopus.local",
                hashed_password="admin",  # В продакшене нужно хешировать
                is_active=True,
                is_admin=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            session.add(admin_user)
            session.commit()
            logger.info("✅ Пользователь администратор создан")
        else:
            logger.info("👤 Пользователи уже существуют")
        
        # Создаем базовые группы (заглушки)
        logger.info("👥 Создаем базовые группы...")
        
        existing_groups = session.query(Group).count()
        if existing_groups == 0:
            # Создаем группы по регионам
            regions = [
                "Малмыж", "Нолинск", "Арбаж", "Нема", "Уржум",
                "Верхошижемье", "Кильмезь", "Пижанка", "Афон",
                "Кукмор", "Советск", "Вятские Поляны", "Лебяжье",
                "Дран", "Балтаси"
            ]
            
            for i, region in enumerate(regions, 1):
                group = Group(
                    name=f"{region} - Инфо",
                    platform="vk",
                    group_id=f"-{100000000 + i}",  # Заглушка ID
                    region=region,
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    settings={
                        "migration_status": "pending",
                        "original_region": region
                    }
                )
                
                session.add(group)
            
            session.commit()
            logger.info(f"✅ Создано {len(regions)} групп")
        else:
            logger.info("👥 Группы уже существуют")
        
        # Создаем базовые расписания
        logger.info("⏰ Создаем базовые расписания...")
        
        existing_schedules = session.query(Schedule).count()
        if existing_schedules == 0:
            schedules = [
                {
                    "name": "Ежедневная публикация",
                    "cron": "0 9 * * *",
                    "description": "Публикация постов каждый день в 9:00"
                },
                {
                    "name": "Еженедельная очистка",
                    "cron": "0 2 * * 0",
                    "description": "Очистка старых данных каждое воскресенье в 2:00"
                }
            ]
            
            for schedule_data in schedules:
                schedule = Schedule(
                    name=schedule_data["name"],
                    cron_expression=schedule_data["cron"],
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    settings={
                        "description": schedule_data["description"],
                        "migration_status": "created"
                    }
                )
                
                session.add(schedule)
            
            session.commit()
            logger.info(f"✅ Создано {len(schedules)} расписаний")
        else:
            logger.info("⏰ Расписания уже существуют")
        
        session.close()
        
        logger.info("🎉 Инициализация базы данных завершена!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка при инициализации базы данных: {e}")
        return False

def main():
    """Главная функция."""
    print("🗄️ Инициализация базы данных PostgreSQL")
    print("=" * 50)
    
    try:
        success = init_database()
        
        if success:
            print("\n✅ База данных успешно инициализирована!")
            print("📋 Создано:")
            print("  - Таблицы PostgreSQL")
            print("  - Пользователь администратор (admin/admin)")
            print("  - Базовые группы по регионам")
            print("  - Базовые расписания")
            print("\n🚀 Готово к миграции данных!")
        else:
            print("\n❌ Ошибка при инициализации базы данных")
            return 1
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
