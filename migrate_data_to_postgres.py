#!/usr/bin/env python3
"""
Скрипт миграции данных из MongoDB в PostgreSQL после развертывания
"""
import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, List
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

class DataMigrator:
    """Мигратор данных из MongoDB в PostgreSQL."""
    
    def __init__(self):
        self.mongo_url = "mongodb+srv://valstan:nitro2000@postopus.qjxr9.mongodb.net/postopus?retryWrites=true&w=majority"
        self.postgres_url = DATABASE_URL
        self.mongo_client = None
        self.mongo_db = None
        self.postgres_engine = None
        self.postgres_session = None
        
        # Статистика миграции
        self.stats = {
            'groups': 0,
            'posts': 0,
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
    
    def migrate_groups(self) -> int:
        """Миграция групп из MongoDB в PostgreSQL."""
        logger.info("👥 Мигрируем группы...")
        
        try:
            # Получаем группы из MongoDB
            config_collection = self.mongo_db['config']
            config_doc = config_collection.find_one({'title': 'config'})
            
            if not config_doc or 'all_my_groups' not in config_doc:
                logger.warning("⚠️ Группы в конфигурации не найдены")
                return 0
            
            groups_data = config_doc['all_my_groups']
            migrated_count = 0
            
            for group_name, group_id in groups_data.items():
                try:
                    # Определяем регион из названия группы
                    region = self._extract_region_from_name(group_name)
                    
                    # Проверяем, существует ли уже группа
                    existing_group = self.postgres_session.query(Group).filter(
                        Group.name == group_name
                    ).first()
                    
                    if existing_group:
                        # Обновляем существующую группу
                        existing_group.group_id = str(group_id)
                        existing_group.region = region
                        existing_group.updated_at = datetime.utcnow()
                        existing_group.settings = {
                            'mongo_source': 'config.all_my_groups',
                            'original_id': group_id,
                            'migrated_at': datetime.utcnow().isoformat()
                        }
                        logger.info(f"  🔄 Обновлена группа: {group_name}")
                    else:
                        # Создаем новую группу
                        group = Group(
                            name=group_name,
                            platform='vk',
                            group_id=str(group_id),
                            region=region,
                            is_active=True,
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow(),
                            settings={
                                'mongo_source': 'config.all_my_groups',
                                'original_id': group_id,
                                'migrated_at': datetime.utcnow().isoformat()
                            }
                        )
                        
                        self.postgres_session.add(group)
                        logger.info(f"  ➕ Создана группа: {group_name}")
                    
                    migrated_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка при миграции группы {group_name}: {e}")
                    self.stats['errors'] += 1
                    continue
            
            self.postgres_session.commit()
            logger.info(f"✅ Мигрировано групп: {migrated_count}")
            return migrated_count
            
        except Exception as e:
            logger.error(f"❌ Ошибка при миграции групп: {e}")
            self.postgres_session.rollback()
            return 0
    
    def migrate_posts(self) -> int:
        """Миграция постов из MongoDB в PostgreSQL."""
        logger.info("📝 Мигрируем посты...")
        
        try:
            # Получаем все коллекции
            collections = self.mongo_db.list_collection_names()
            post_collections = [col for col in collections if col not in [
                'users', 'settings', 'logs', 'statistics', 'health_checks', 
                'task_executions', 'tasks', 'config', 'deserter', 'bal'
            ]]
            
            migrated_count = 0
            
            for collection_name in post_collections:
                logger.info(f"  📄 Обрабатываем коллекцию: {collection_name}")
                
                collection = self.mongo_db[collection_name]
                documents = list(collection.find({}))
                
                for doc in documents:
                    try:
                        # Создаем пост
                        post = self._create_post_from_document(doc, collection_name)
                        
                        if post:
                            self.postgres_session.add(post)
                            migrated_count += 1
                            
                    except Exception as e:
                        logger.error(f"❌ Ошибка при миграции поста из {collection_name}: {e}")
                        self.stats['errors'] += 1
                        continue
                
                logger.info(f"  ✅ Коллекция {collection_name}: {len(documents)} постов")
            
            self.postgres_session.commit()
            logger.info(f"✅ Мигрировано постов: {migrated_count}")
            return migrated_count
            
        except Exception as e:
            logger.error(f"❌ Ошибка при миграции постов: {e}")
            self.postgres_session.rollback()
            return 0
    
    def _extract_region_from_name(self, group_name: str) -> str:
        """Извлечение региона из названия группы."""
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
    
    def _create_post_from_document(self, doc: Dict[str, Any], collection_name: str) -> Post:
        """Создание объекта Post из документа MongoDB."""
        try:
            # Извлекаем текст поста
            content = ""
            if 'lip' in doc and isinstance(doc['lip'], list):
                content = " ".join(str(item) for item in doc['lip'])
            elif 'text' in doc:
                content = str(doc['text'])
            elif 'content' in doc:
                content = str(doc['content'])
            
            # Создаем заголовок
            title = doc.get('title', f'Post from {collection_name}')
            
            # Извлекаем группы
            vk_groups = []
            if 'post_group_vk' in doc:
                vk_groups = doc['post_group_vk'] if isinstance(doc['post_group_vk'], list) else [doc['post_group_vk']]
            
            telegram_groups = []
            if 'post_group_telega' in doc:
                telegram_groups = doc['post_group_telega'] if isinstance(doc['post_group_telega'], list) else [doc['post_group_telega']]
            
            # Создаем пост
            post = Post(
                title=title,
                content=content,
                image_url=None,
                video_url=None,
                status='published',
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                scheduled_at=None,
                published_at=datetime.utcnow(),
                vk_group_id=str(vk_groups[0]) if vk_groups else None,
                telegram_chat_id=str(telegram_groups[0]) if telegram_groups else None,
                region=self._extract_region_from_name(collection_name),
                source_collection=collection_name,
                metadata={
                    'mongo_collection': collection_name,
                    'mongo_id': str(doc.get('_id')),
                    'vk_groups': vk_groups,
                    'telegram_groups': telegram_groups,
                    'migrated_at': datetime.utcnow().isoformat(),
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
    
    def run_migration(self) -> Dict[str, int]:
        """Запуск полной миграции."""
        logger.info("🚀 Начинаем миграцию данных...")
        
        # Подключаемся к базам данных
        if not self.connect_mongo():
            raise Exception("Не удалось подключиться к MongoDB")
        
        if not self.connect_postgres():
            raise Exception("Не удалось подключиться к PostgreSQL")
        
        # Выполняем миграцию
        self.stats['groups'] = self.migrate_groups()
        self.stats['posts'] = self.migrate_posts()
        
        # Закрываем соединения
        if self.mongo_client:
            self.mongo_client.close()
        if self.postgres_session:
            self.postgres_session.close()
        
        logger.info("🎉 Миграция завершена!")
        return self.stats

def main():
    """Главная функция."""
    print("🔄 Миграция данных из MongoDB в PostgreSQL")
    print("=" * 60)
    
    try:
        # Создаем мигратор
        migrator = DataMigrator()
        
        # Запускаем миграцию
        results = migrator.run_migration()
        
        # Выводим результаты
        print("\n📊 РЕЗУЛЬТАТЫ МИГРАЦИИ:")
        print("-" * 40)
        print(f"👥 Групп мигрировано: {results['groups']}")
        print(f"📝 Постов мигрировано: {results['posts']}")
        if results['errors'] > 0:
            print(f"❌ Ошибок: {results['errors']}")
        
        total = results['groups'] + results['posts']
        print(f"\n✅ Всего записей мигрировано: {total}")
        
        if total > 0:
            print("\n🎉 Миграция успешно завершена!")
            print("🌐 Проверьте данные в веб-интерфейсе")
        else:
            print("\n⚠️ Данные не были мигрированы")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при миграции: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
