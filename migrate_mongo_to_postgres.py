#!/usr/bin/env python3
"""
Скрипт миграции данных из MongoDB в PostgreSQL для PostOpus.
"""
import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    from src.web.models import Post, Group, Schedule, User, Base
    from src.web.database import DATABASE_URL
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Установите зависимости: pip install pymongo sqlalchemy psycopg2-binary")
    sys.exit(1)

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MongoToPostgresMigrator:
    """Класс для миграции данных из MongoDB в PostgreSQL."""
    
    def __init__(self, mongo_url: str, postgres_url: str):
        self.mongo_url = mongo_url
        self.postgres_url = postgres_url
        self.mongo_client = None
        self.mongo_db = None
        self.postgres_engine = None
        self.postgres_session = None
        
    def connect_mongo(self) -> bool:
        """Подключение к MongoDB."""
        try:
            self.mongo_client = MongoClient(self.mongo_url)
            self.mongo_db = self.mongo_client['postopus']
            
            # Тестируем соединение
            self.mongo_client.admin.command('ping')
            logger.info("✅ Подключение к MongoDB успешно")
            return True
        except ConnectionFailure as e:
            logger.error(f"❌ Ошибка подключения к MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка при подключении к MongoDB: {e}")
            return False
    
    def connect_postgres(self) -> bool:
        """Подключение к PostgreSQL."""
        try:
            self.postgres_engine = create_engine(self.postgres_url, echo=False)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.postgres_engine)
            self.postgres_session = SessionLocal()
            
            # Тестируем соединение
            with self.postgres_engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                logger.info("✅ Подключение к PostgreSQL успешно")
                return True
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к PostgreSQL: {e}")
            return False
    
    def migrate_posts(self) -> int:
        """Миграция постов из MongoDB в PostgreSQL."""
        logger.info("🔄 Начинаем миграцию постов...")
        
        try:
            # Получаем коллекции постов из MongoDB
            collections = self.mongo_db.list_collection_names()
            post_collections = [col for col in collections if col not in ['users', 'settings', 'logs', 'statistics', 'health_checks', 'task_executions', 'tasks', 'config', 'deserter', 'bal']]
            
            migrated_count = 0
            
            for collection_name in post_collections:
                logger.info(f"📄 Обрабатываем коллекцию: {collection_name}")
                collection = self.mongo_db[collection_name]
                
                # Получаем все документы из коллекции
                documents = list(collection.find({}))
                
                for doc in documents:
                    try:
                        # Создаем объект Post для PostgreSQL
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
                                'mongo_id': str(doc.get('_id')),
                                'original_data': {k: v for k, v in doc.items() if k not in ['_id', 'title', 'text', 'content', 'image', 'image_url', 'video', 'video_url', 'status', 'created_at', 'updated_at', 'scheduled_at', 'published_at', 'group_id', 'vk_group_id', 'telegram_chat_id']}
                            }
                        )
                        
                        self.postgres_session.add(post)
                        migrated_count += 1
                        
                    except Exception as e:
                        logger.error(f"❌ Ошибка при миграции документа из {collection_name}: {e}")
                        continue
                
                logger.info(f"✅ Коллекция {collection_name} обработана")
            
            # Сохраняем изменения
            self.postgres_session.commit()
            logger.info(f"✅ Миграция постов завершена. Перенесено: {migrated_count} постов")
            return migrated_count
            
        except Exception as e:
            logger.error(f"❌ Ошибка при миграции постов: {e}")
            self.postgres_session.rollback()
            return 0
    
    def migrate_groups(self) -> int:
        """Миграция групп из конфигурации MongoDB в PostgreSQL."""
        logger.info("🔄 Начинаем миграцию групп...")
        
        try:
            migrated_count = 0
            
            # Получаем конфигурацию групп
            config_collection = self.mongo_db['config']
            config_doc = config_collection.find_one({'title': 'config'})
            
            if config_doc and 'all_my_groups' in config_doc:
                groups_data = config_doc['all_my_groups']
                
                for group_name, group_id in groups_data.items():
                    try:
                        # Создаем объект Group для PostgreSQL
                        group = Group(
                            name=group_name,
                            platform='vk',  # Предполагаем VK
                            group_id=str(group_id),
                            access_token=None,  # Токены хранятся отдельно
                            is_active=True,
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow(),
                            settings={
                                'mongo_source': 'config.all_my_groups',
                                'original_id': group_id
                            }
                        )
                        
                        self.postgres_session.add(group)
                        migrated_count += 1
                        
                    except Exception as e:
                        logger.error(f"❌ Ошибка при миграции группы {group_name}: {e}")
                        continue
            
            # Сохраняем изменения
            self.postgres_session.commit()
            logger.info(f"✅ Миграция групп завершена. Перенесено: {migrated_count} групп")
            return migrated_count
            
        except Exception as e:
            logger.error(f"❌ Ошибка при миграции групп: {e}")
            self.postgres_session.rollback()
            return 0
    
    def migrate_users(self) -> int:
        """Миграция пользователей из MongoDB в PostgreSQL."""
        logger.info("🔄 Начинаем миграцию пользователей...")
        
        try:
            migrated_count = 0
            
            # Получаем пользователей из MongoDB
            users_collection = self.mongo_db['users']
            users = list(users_collection.find({}))
            
            for user_doc in users:
                try:
                    # Создаем объект User для PostgreSQL
                    user = User(
                        username=user_doc.get('username', ''),
                        email=user_doc.get('email', ''),
                        hashed_password=user_doc.get('hashed_password', ''),
                        is_active=user_doc.get('is_active', True),
                        is_admin=user_doc.get('is_admin', False),
                        created_at=user_doc.get('created_at', datetime.utcnow()),
                        updated_at=user_doc.get('updated_at', datetime.utcnow())
                    )
                    
                    self.postgres_session.add(user)
                    migrated_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка при миграции пользователя: {e}")
                    continue
            
            # Если пользователей нет, создаем администратора по умолчанию
            if migrated_count == 0:
                logger.info("📝 Создаем пользователя администратора по умолчанию...")
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
                
                self.postgres_session.add(admin_user)
                migrated_count = 1
            
            # Сохраняем изменения
            self.postgres_session.commit()
            logger.info(f"✅ Миграция пользователей завершена. Перенесено: {migrated_count} пользователей")
            return migrated_count
            
        except Exception as e:
            logger.error(f"❌ Ошибка при миграции пользователей: {e}")
            self.postgres_session.rollback()
            return 0
    
    def migrate_schedules(self) -> int:
        """Миграция расписаний из MongoDB в PostgreSQL."""
        logger.info("🔄 Начинаем миграцию расписаний...")
        
        try:
            migrated_count = 0
            
            # Получаем задачи из MongoDB
            tasks_collection = self.mongo_db['tasks']
            tasks = list(tasks_collection.find({}))
            
            for task_doc in tasks:
                try:
                    # Создаем объект Schedule для PostgreSQL
                    schedule = Schedule(
                        name=task_doc.get('name', f'Task {task_doc.get("id", "unknown")}'),
                        cron_expression=task_doc.get('cron', '0 0 * * *'),  # По умолчанию ежедневно
                        is_active=task_doc.get('enabled', True),
                        created_at=task_doc.get('created_at', datetime.utcnow()),
                        updated_at=task_doc.get('updated_at', datetime.utcnow()),
                        last_run=task_doc.get('last_run'),
                        next_run=task_doc.get('next_run'),
                        settings={
                            'mongo_id': str(task_doc.get('_id')),
                            'original_data': task_doc
                        }
                    )
                    
                    self.postgres_session.add(schedule)
                    migrated_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка при миграции задачи: {e}")
                    continue
            
            # Сохраняем изменения
            self.postgres_session.commit()
            logger.info(f"✅ Миграция расписаний завершена. Перенесено: {migrated_count} расписаний")
            return migrated_count
            
        except Exception as e:
            logger.error(f"❌ Ошибка при миграции расписаний: {e}")
            self.postgres_session.rollback()
            return 0
    
    def create_tables(self):
        """Создание таблиц в PostgreSQL."""
        logger.info("🔄 Создаем таблицы в PostgreSQL...")
        try:
            Base.metadata.create_all(bind=self.postgres_engine)
            logger.info("✅ Таблицы созданы успешно")
        except Exception as e:
            logger.error(f"❌ Ошибка при создании таблиц: {e}")
            raise
    
    def run_migration(self) -> Dict[str, int]:
        """Запуск полной миграции."""
        logger.info("🚀 Начинаем миграцию данных из MongoDB в PostgreSQL...")
        
        # Подключаемся к базам данных
        if not self.connect_mongo():
            raise Exception("Не удалось подключиться к MongoDB")
        
        if not self.connect_postgres():
            raise Exception("Не удалось подключиться к PostgreSQL")
        
        # Создаем таблицы
        self.create_tables()
        
        # Выполняем миграцию
        results = {
            'posts': self.migrate_posts(),
            'groups': self.migrate_groups(),
            'users': self.migrate_users(),
            'schedules': self.migrate_schedules()
        }
        
        # Закрываем соединения
        if self.mongo_client:
            self.mongo_client.close()
        if self.postgres_session:
            self.postgres_session.close()
        
        logger.info("🎉 Миграция завершена!")
        return results

def main():
    """Главная функция."""
    print("🔄 Скрипт миграции данных из MongoDB в PostgreSQL")
    print("=" * 60)
    
    # Получаем параметры подключения
    mongo_url = input("Введите URL MongoDB (например: mongodb://user:pass@host:port/): ").strip()
    if not mongo_url:
        print("❌ URL MongoDB не может быть пустым")
        return
    
    # URL PostgreSQL из переменных окружения или ввод пользователя
    postgres_url = os.getenv('DATABASE_URL', DATABASE_URL)
    if not postgres_url or postgres_url == DATABASE_URL:
        postgres_url = input("Введите URL PostgreSQL (например: postgresql://user:pass@host:port/db): ").strip()
        if not postgres_url:
            print("❌ URL PostgreSQL не может быть пустым")
            return
    
    try:
        # Создаем мигратор
        migrator = MongoToPostgresMigrator(mongo_url, postgres_url)
        
        # Запускаем миграцию
        results = migrator.run_migration()
        
        # Выводим результаты
        print("\n📊 Результаты миграции:")
        print("-" * 30)
        for table, count in results.items():
            print(f"  {table}: {count} записей")
        
        total = sum(results.values())
        print(f"\n✅ Всего перенесено: {total} записей")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при выполнении миграции: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
