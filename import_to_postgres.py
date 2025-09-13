#!/usr/bin/env python3
"""
Скрипт для импорта данных из JSON файлов в PostgreSQL.
"""
import json
import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, List
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

def import_to_postgres(json_file: str, postgres_url: str = None):
    """Импорт данных из JSON файла в PostgreSQL."""
    
    try:
        # Подключаемся к PostgreSQL
        if not postgres_url:
            postgres_url = DATABASE_URL
            
        engine = create_engine(postgres_url, echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        
        # Тестируем соединение
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info("✅ Подключение к PostgreSQL успешно")
        
        # Создаем таблицы
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Таблицы созданы/проверены")
        
        # Загружаем JSON данные
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"📄 Загружен файл: {json_file}")
        logger.info(f"📅 Дата экспорта: {data.get('export_timestamp', 'неизвестно')}")
        
        imported_counts = {
            'posts': 0,
            'groups': 0,
            'users': 0,
            'schedules': 0
        }
        
        # Обрабатываем коллекции
        collections = data.get('collections', {})
        
        # Импортируем посты
        logger.info("🔄 Импортируем посты...")
        for collection_name, documents in collections.items():
            if collection_name in ['users', 'settings', 'logs', 'statistics', 'health_checks', 'task_executions', 'tasks', 'config', 'deserter', 'bal']:
                continue
                
            logger.info(f"📄 Обрабатываем коллекцию постов: {collection_name}")
            
            for doc in documents:
                try:
                    post = Post(
                        title=doc.get('title', f'Post from {collection_name}'),
                        content=doc.get('text', doc.get('content', '')),
                        image_url=doc.get('image_url', doc.get('image', '')),
                        video_url=doc.get('video_url', doc.get('video', '')),
                        status=doc.get('status', 'draft'),
                        created_at=doc.get('created_at', datetime.utcnow()),
                        updated_at=doc.get('updated_at', datetime.utcnow()),
                        scheduled_at=doc.get('scheduled_at'),
                        published_at=doc.get('published_at'),
                        vk_group_id=doc.get('vk_group_id', doc.get('group_id')),
                        telegram_chat_id=doc.get('telegram_chat_id'),
                        metadata={
                            'mongo_collection': collection_name,
                            'mongo_id': str(doc.get('_id', '')),
                            'original_data': {k: v for k, v in doc.items() if k not in ['_id', 'title', 'text', 'content', 'image', 'image_url', 'video', 'video_url', 'status', 'created_at', 'updated_at', 'scheduled_at', 'published_at', 'group_id', 'vk_group_id', 'telegram_chat_id']}
                        }
                    )
                    
                    session.add(post)
                    imported_counts['posts'] += 1
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка при импорте поста: {e}")
                    continue
        
        # Импортируем группы из конфигурации
        logger.info("🔄 Импортируем группы...")
        config_doc = collections.get('config', [])
        if config_doc:
            config_data = config_doc[0] if isinstance(config_doc, list) else config_doc
            if 'all_my_groups' in config_data:
                groups_data = config_data['all_my_groups']
                
                for group_name, group_id in groups_data.items():
                    try:
                        group = Group(
                            name=group_name,
                            platform='vk',
                            group_id=str(group_id),
                            access_token=None,
                            is_active=True,
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow(),
                            settings={
                                'mongo_source': 'config.all_my_groups',
                                'original_id': group_id
                            }
                        )
                        
                        session.add(group)
                        imported_counts['groups'] += 1
                        
                    except Exception as e:
                        logger.error(f"❌ Ошибка при импорте группы {group_name}: {e}")
                        continue
        
        # Импортируем пользователей
        logger.info("🔄 Импортируем пользователей...")
        users_data = collections.get('users', [])
        if users_data:
            for user_doc in users_data:
                try:
                    user = User(
                        username=user_doc.get('username', ''),
                        email=user_doc.get('email', ''),
                        hashed_password=user_doc.get('hashed_password', ''),
                        is_active=user_doc.get('is_active', True),
                        is_admin=user_doc.get('is_admin', False),
                        created_at=user_doc.get('created_at', datetime.utcnow()),
                        updated_at=user_doc.get('updated_at', datetime.utcnow())
                    )
                    
                    session.add(user)
                    imported_counts['users'] += 1
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка при импорте пользователя: {e}")
                    continue
        
        # Если пользователей нет, создаем администратора
        if imported_counts['users'] == 0:
            logger.info("📝 Создаем пользователя администратора по умолчанию...")
            try:
                from passlib.context import CryptContext
                pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                
                admin_user = User(
                    username="admin",
                    email="admin@postopus.local",
                    hashed_password=pwd_context.hash("admin"),
                    is_active=True,
                    is_admin=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                session.add(admin_user)
                imported_counts['users'] = 1
                
            except ImportError:
                logger.warning("⚠️ passlib не установлен, создаем пользователя без хеширования пароля")
                admin_user = User(
                    username="admin",
                    email="admin@postopus.local",
                    hashed_password="admin",  # Небезопасно, но для тестирования
                    is_active=True,
                    is_admin=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                session.add(admin_user)
                imported_counts['users'] = 1
        
        # Импортируем расписания
        logger.info("🔄 Импортируем расписания...")
        tasks_data = collections.get('tasks', [])
        for task_doc in tasks_data:
            try:
                schedule = Schedule(
                    name=task_doc.get('name', f'Task {task_doc.get("id", "unknown")}'),
                    cron_expression=task_doc.get('cron', '0 0 * * *'),
                    is_active=task_doc.get('enabled', True),
                    created_at=task_doc.get('created_at', datetime.utcnow()),
                    updated_at=task_doc.get('updated_at', datetime.utcnow()),
                    last_run=task_doc.get('last_run'),
                    next_run=task_doc.get('next_run'),
                    settings={
                        'mongo_id': str(task_doc.get('_id', '')),
                        'original_data': task_doc
                    }
                )
                
                session.add(schedule)
                imported_counts['schedules'] += 1
                
            except Exception as e:
                logger.error(f"❌ Ошибка при импорте задачи: {e}")
                continue
        
        # Сохраняем изменения
        session.commit()
        session.close()
        
        logger.info("✅ Импорт завершен успешно!")
        return imported_counts
        
    except Exception as e:
        logger.error(f"❌ Ошибка при импорте: {e}")
        return None

def main():
    """Главная функция."""
    print("📥 Скрипт импорта данных в PostgreSQL")
    print("=" * 50)
    
    # Получаем путь к JSON файлу
    json_file = input("Введите путь к JSON файлу с данными: ").strip()
    if not json_file or not os.path.exists(json_file):
        print("❌ Файл не найден")
        return
    
    # Получаем URL PostgreSQL (опционально)
    postgres_url = input("Введите URL PostgreSQL (Enter для использования по умолчанию): ").strip()
    if not postgres_url:
        postgres_url = None
    
    # Запускаем импорт
    results = import_to_postgres(json_file, postgres_url)
    
    if results:
        print("\n📊 Результаты импорта:")
        print("-" * 30)
        for table, count in results.items():
            print(f"  {table}: {count} записей")
        
        total = sum(results.values())
        print(f"\n✅ Всего импортировано: {total} записей")
    else:
        print("\n❌ Ошибка при импорте данных")

if __name__ == "__main__":
    main()
