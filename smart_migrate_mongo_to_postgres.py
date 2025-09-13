#!/usr/bin/env python3
"""
Умный скрипт миграции данных из MongoDB в PostgreSQL на основе анализа структуры данных.
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.web.models import Post, Group, Schedule, User, Base
from src.web.database import DATABASE_URL

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SmartMongoToPostgresMigrator:
    """Умный мигратор данных из MongoDB в PostgreSQL."""
    
    def __init__(self, mongo_url: str, postgres_url: str = None):
        self.mongo_url = mongo_url
        self.postgres_url = postgres_url or DATABASE_URL
        self.mongo_client = None
        self.mongo_db = None
        self.postgres_engine = None
        self.postgres_session = None
        
        # Результаты миграции
        self.migration_stats = {
            'posts': 0,
            'groups': 0,
            'users': 0,
            'schedules': 0,
            'errors': 0
        }
        
    def connect_mongo(self) -> bool:
        """Подключение к MongoDB."""
        try:
            self.mongo_client = MongoClient(self.mongo_url)
            self.mongo_db = self.mongo_client['postopus']
            self.mongo_client.admin.command('ping')
            logger.info("✅ Подключение к MongoDB успешно")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к MongoDB: {e}")
            return False
    
    def connect_postgres(self) -> bool:
        """Подключение к PostgreSQL."""
        try:
            self.postgres_engine = create_engine(self.postgres_url, echo=False)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.postgres_engine)
            self.postgres_session = SessionLocal()
            
            with self.postgres_engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                logger.info("✅ Подключение к PostgreSQL успешно")
                return True
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к PostgreSQL: {e}")
            return False
    
    def create_tables(self):
        """Создание таблиц в PostgreSQL."""
        logger.info("🔄 Создаем таблицы в PostgreSQL...")
        try:
            Base.metadata.create_all(bind=self.postgres_engine)
            logger.info("✅ Таблицы созданы успешно")
        except Exception as e:
            logger.error(f"❌ Ошибка при создании таблиц: {e}")
            raise
    
    def migrate_groups_from_config(self) -> int:
        """Миграция групп из конфигурации."""
        logger.info("👥 Мигрируем группы из конфигурации...")
        
        try:
            config_collection = self.mongo_db['config']
            config_doc = config_collection.find_one({'title': 'config'})
            
            if not config_doc or 'all_my_groups' not in config_doc:
                logger.warning("⚠️ Группы в конфигурации не найдены")
                return 0
            
            groups_data = config_doc['all_my_groups']
            migrated_count = 0
            
            for group_name, group_id in groups_data.items():
                try:
                    # Определяем платформу по ID группы
                    platform = 'vk' if str(group_id).startswith('-') else 'vk'
                    
                    group = Group(
                        name=group_name,
                        platform=platform,
                        group_id=str(group_id),
                        access_token=None,
                        is_active=True,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                        settings={
                            'mongo_source': 'config.all_my_groups',
                            'original_id': group_id,
                            'region': self._extract_region_from_group_name(group_name)
                        }
                    )
                    
                    self.postgres_session.add(group)
                    migrated_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка при миграции группы {group_name}: {e}")
                    self.migration_stats['errors'] += 1
                    continue
            
            self.postgres_session.commit()
            logger.info(f"✅ Мигрировано групп: {migrated_count}")
            return migrated_count
            
        except Exception as e:
            logger.error(f"❌ Ошибка при миграции групп: {e}")
            self.postgres_session.rollback()
            return 0
    
    def _extract_region_from_group_name(self, group_name: str) -> str:
        """Извлечение региона из названия группы."""
        # Простая логика определения региона
        region_mapping = {
            'mi': 'Малмыж',
            'nolinsk': 'Нолинск',
            'arbazh': 'Арбаж',
            'nema': 'Нема',
            'ur': 'Уржум',
            'verhoshizhem': 'Верхошижемье',
            'klz': 'Кильмезь',
            'pizhanka': 'Пижанка',
            'kukmor': 'Кукмор',
            'sovetsk': 'Советск',
            'vp': 'Вятские Поляны',
            'leb': 'Лебяжье',
            'dran': 'Дран',
            'bal': 'Балтаси'
        }
        
        for key, region in region_mapping.items():
            if key in group_name.lower():
                return region
        
        return group_name
    
    def migrate_posts_from_collections(self) -> int:
        """Миграция постов из всех коллекций."""
        logger.info("📝 Мигрируем посты из коллекций...")
        
        try:
            # Получаем все коллекции
            collections = self.mongo_db.list_collection_names()
            
            # Исключаем служебные коллекции
            post_collections = [col for col in collections if col not in [
                'users', 'settings', 'logs', 'statistics', 'health_checks', 
                'task_executions', 'tasks', 'config', 'deserter', 'bal'
            ]]
            
            migrated_count = 0
            
            for collection_name in post_collections:
                logger.info(f"📄 Обрабатываем коллекцию: {collection_name}")
                
                collection = self.mongo_db[collection_name]
                documents = list(collection.find({}))
                
                for doc in documents:
                    try:
                        # Создаем пост на основе структуры данных
                        post = self._create_post_from_document(doc, collection_name)
                        
                        if post:
                            self.postgres_session.add(post)
                            migrated_count += 1
                            
                    except Exception as e:
                        logger.error(f"❌ Ошибка при миграции поста из {collection_name}: {e}")
                        self.migration_stats['errors'] += 1
                        continue
                
                logger.info(f"✅ Коллекция {collection_name} обработана")
            
            self.postgres_session.commit()
            logger.info(f"✅ Мигрировано постов: {migrated_count}")
            return migrated_count
            
        except Exception as e:
            logger.error(f"❌ Ошибка при миграции постов: {e}")
            self.postgres_session.rollback()
            return 0
    
    def _create_post_from_document(self, doc: Dict[str, Any], collection_name: str) -> Optional[Post]:
        """Создание объекта Post из документа MongoDB."""
        try:
            # Извлекаем текст поста из поля 'lip' (основное содержимое)
            content = ""
            if 'lip' in doc and isinstance(doc['lip'], list):
                content = " ".join(str(item) for item in doc['lip'])
            elif 'text' in doc:
                content = str(doc['text'])
            elif 'content' in doc:
                content = str(doc['content'])
            
            # Создаем заголовок
            title = doc.get('title', f'Post from {collection_name}')
            
            # Определяем статус
            status = 'published'  # Предполагаем, что все посты опубликованы
            
            # Извлекаем группы VK
            vk_groups = []
            if 'post_group_vk' in doc:
                vk_groups = doc['post_group_vk'] if isinstance(doc['post_group_vk'], list) else [doc['post_group_vk']]
            
            # Извлекаем группы Telegram
            telegram_groups = []
            if 'post_group_telega' in doc:
                telegram_groups = doc['post_group_telega'] if isinstance(doc['post_group_telega'], list) else [doc['post_group_telega']]
            
            # Создаем пост
            post = Post(
                title=title,
                content=content,
                image_url=None,  # В данной структуре нет изображений
                video_url=None,  # В данной структуре нет видео
                status=status,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                scheduled_at=None,
                published_at=datetime.utcnow(),
                vk_group_id=str(vk_groups[0]) if vk_groups else None,
                telegram_chat_id=str(telegram_groups[0]) if telegram_groups else None,
                metadata={
                    'mongo_collection': collection_name,
                    'mongo_id': str(doc.get('_id')),
                    'region': self._extract_region_from_group_name(collection_name),
                    'vk_groups': vk_groups,
                    'telegram_groups': telegram_groups,
                    'original_data': {
                        k: v for k, v in doc.items() 
                        if k not in ['_id', 'title', 'lip', 'text', 'content', 'post_group_vk', 'post_group_telega']
                    }
                }
            )
            
            return post
            
        except Exception as e:
            logger.error(f"❌ Ошибка при создании поста: {e}")
            return None
    
    def create_default_admin_user(self) -> int:
        """Создание пользователя администратора по умолчанию."""
        logger.info("👤 Создаем пользователя администратора по умолчанию...")
        
        try:
            # Проверяем, есть ли уже пользователи
            existing_users = self.postgres_session.query(User).count()
            if existing_users > 0:
                logger.info("👤 Пользователи уже существуют, пропускаем создание")
                return 0
            
            # Создаем администратора
            admin_user = User(
                username="admin",
                email="admin@postopus.local",
                hashed_password="admin",  # В продакшене нужно хешировать
                is_active=True,
                is_admin=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.postgres_session.add(admin_user)
            self.postgres_session.commit()
            
            logger.info("✅ Пользователь администратор создан")
            return 1
            
        except Exception as e:
            logger.error(f"❌ Ошибка при создании пользователя: {e}")
            self.postgres_session.rollback()
            return 0
    
    def migrate_schedules_from_tasks(self) -> int:
        """Миграция расписаний из задач."""
        logger.info("⏰ Мигрируем расписания из задач...")
        
        try:
            tasks_collection = self.mongo_db['tasks']
            tasks = list(tasks_collection.find({}))
            
            if not tasks:
                logger.info("⚠️ Задачи не найдены")
                return 0
            
            migrated_count = 0
            
            for task_doc in tasks:
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
                            'mongo_id': str(task_doc.get('_id')),
                            'original_data': task_doc
                        }
                    )
                    
                    self.postgres_session.add(schedule)
                    migrated_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка при миграции задачи: {e}")
                    self.migration_stats['errors'] += 1
                    continue
            
            self.postgres_session.commit()
            logger.info(f"✅ Мигрировано расписаний: {migrated_count}")
            return migrated_count
            
        except Exception as e:
            logger.error(f"❌ Ошибка при миграции расписаний: {e}")
            self.postgres_session.rollback()
            return 0
    
    def run_migration(self) -> Dict[str, int]:
        """Запуск полной миграции."""
        logger.info("🚀 Начинаем умную миграцию данных...")
        
        # Подключаемся к базам данных
        if not self.connect_mongo():
            raise Exception("Не удалось подключиться к MongoDB")
        
        if not self.connect_postgres():
            raise Exception("Не удалось подключиться к PostgreSQL")
        
        # Создаем таблицы
        self.create_tables()
        
        # Выполняем миграцию
        self.migration_stats['groups'] = self.migrate_groups_from_config()
        self.migration_stats['posts'] = self.migrate_posts_from_collections()
        self.migration_stats['users'] = self.create_default_admin_user()
        self.migration_stats['schedules'] = self.migrate_schedules_from_tasks()
        
        # Закрываем соединения
        if self.mongo_client:
            self.mongo_client.close()
        if self.postgres_session:
            self.postgres_session.close()
        
        logger.info("🎉 Миграция завершена!")
        return self.migration_stats

def main():
    """Главная функция."""
    print("🧠 Умная миграция данных из MongoDB в PostgreSQL")
    print("=" * 60)
    
    # URL MongoDB
    mongo_url = "mongodb+srv://valstan:nitro2000@postopus.qjxr9.mongodb.net/postopus?retryWrites=true&w=majority"
    
    # URL PostgreSQL (можно изменить)
    postgres_url = input("Введите URL PostgreSQL (Enter для использования по умолчанию): ").strip()
    if not postgres_url:
        postgres_url = None
    
    try:
        # Создаем мигратор
        migrator = SmartMongoToPostgresMigrator(mongo_url, postgres_url)
        
        # Запускаем миграцию
        results = migrator.run_migration()
        
        # Выводим результаты
        print("\n📊 РЕЗУЛЬТАТЫ МИГРАЦИИ:")
        print("-" * 40)
        for table, count in results.items():
            if table != 'errors':
                print(f"  {table}: {count} записей")
        
        if results['errors'] > 0:
            print(f"  ⚠️ ошибок: {results['errors']}")
        
        total = sum(v for k, v in results.items() if k != 'errors')
        print(f"\n✅ Всего перенесено: {total} записей")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при выполнении миграции: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
