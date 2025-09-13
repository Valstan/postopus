#!/usr/bin/env python3
"""
Скрипт инициализации тестовых данных для PostOpus.
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
    from src.web.config import Config
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Установите зависимости: pip install sqlalchemy psycopg2-binary")
    sys.exit(1)

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_test_data():
    """Инициализация тестовых данных."""
    logger.info("🗄️ Инициализируем тестовые данные...")
    
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
        
        # Создаем группы
        logger.info("👥 Создаем группы...")
        
        existing_groups = session.query(Group).count()
        if existing_groups == 0:
            # Создаем группы по регионам
            for i, region in enumerate(Config.REGIONS, 1):
                group = Group(
                    name=f"{region} - Инфо",
                    platform="vk",
                    group_id=f"-{100000000 + i}",  # Заглушка ID
                    region=region,
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    settings={
                        "migration_status": "created",
                        "original_region": region,
                        "vk_tokens": Config.get_active_vk_tokens()
                    }
                )
                
                session.add(group)
            
            session.commit()
            logger.info(f"✅ Создано {len(Config.REGIONS)} групп")
        else:
            logger.info("👥 Группы уже существуют")
        
        # Создаем тестовые посты
        logger.info("📝 Создаем тестовые посты...")
        
        existing_posts = session.query(Post).count()
        if existing_posts == 0:
            # Создаем тестовые посты для каждого региона
            test_posts = [
                {
                    "title": "Новости региона",
                    "content": "Важные новости и события в регионе",
                    "region": "Малмыж",
                    "status": "published"
                },
                {
                    "title": "Объявления",
                    "content": "Полезные объявления для жителей",
                    "region": "Нолинск",
                    "status": "published"
                },
                {
                    "title": "События",
                    "content": "Культурные и спортивные события",
                    "region": "Арбаж",
                    "status": "published"
                },
                {
                    "title": "Планируется к публикации",
                    "content": "Пост в очереди на публикацию",
                    "region": "Уржум",
                    "status": "scheduled"
                },
                {
                    "title": "Черновик",
                    "content": "Пост в процессе редактирования",
                    "region": "Кильмезь",
                    "status": "draft"
                }
            ]
            
            for post_data in test_posts:
                post = Post(
                    title=post_data["title"],
                    content=post_data["content"],
                    region=post_data["region"],
                    source_collection=post_data["region"].lower().replace(" ", "_"),
                    status=post_data["status"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    published_at=datetime.utcnow() if post_data["status"] == "published" else None,
                    scheduled_at=datetime.utcnow() if post_data["status"] == "scheduled" else None,
                    meta_data={
                        "test_data": True,
                        "created_by": "init_script",
                        "region": post_data["region"]
                    }
                )
                
                session.add(post)
            
            session.commit()
            logger.info(f"✅ Создано {len(test_posts)} тестовых постов")
        else:
            logger.info("📝 Посты уже существуют")
        
        # Создаем расписания
        logger.info("⏰ Создаем расписания...")
        
        existing_schedules = session.query(Schedule).count()
        if existing_schedules == 0:
            # Создаем расписания на основе конфигурации
            schedules = [
                {
                    "name": "Новости Малмыж",
                    "cron": "05 7,8,10,12,14-23 * * *",
                    "description": "Публикация новостей Малмыж"
                },
                {
                    "name": "Реклама Малмыж",
                    "cron": "15 9,13 * * *",
                    "description": "Публикация рекламы Малмыж"
                },
                {
                    "name": "Новости Дран",
                    "cron": "25 7,9,12,18,20,22 * * *",
                    "description": "Публикация новостей Дран"
                },
                {
                    "name": "Сбор рекламы",
                    "cron": "40 5-22 * * *",
                    "description": "Автоматический сбор рекламы"
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
                        "migration_status": "created",
                        "original_cron": schedule_data["cron"]
                    }
                )
                
                session.add(schedule)
            
            session.commit()
            logger.info(f"✅ Создано {len(schedules)} расписаний")
        else:
            logger.info("⏰ Расписания уже существуют")
        
        session.close()
        
        logger.info("🎉 Тестовые данные успешно инициализированы!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка при инициализации тестовых данных: {e}")
        return False

def main():
    """Главная функция."""
    print("🗄️ Инициализация тестовых данных PostOpus")
    print("=" * 50)
    
    try:
        success = init_test_data()
        
        if success:
            print("\n✅ Тестовые данные успешно инициализированы!")
            print("📋 Создано:")
            print("  - Пользователь администратор (admin/admin)")
            print(f"  - {len(Config.REGIONS)} групп по регионам")
            print("  - 5 тестовых постов")
            print("  - 4 расписания задач")
            print("\n🌐 Теперь можно тестировать веб-интерфейс!")
            print("📊 Дашборд: https://your-app.onrender.com")
            print("🧪 Тест API: https://your-app.onrender.com/test")
        else:
            print("\n❌ Ошибка при инициализации тестовых данных")
            return 1
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
