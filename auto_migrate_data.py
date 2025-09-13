#!/usr/bin/env python3
"""
Автоматическая миграция данных после развертывания на Render.com
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoMigrator:
    """Автоматический мигратор данных."""
    
    def __init__(self):
        self.mongo_url = "mongodb+srv://valstan:nitro2000@postopus.qjxr9.mongodb.net/postopus?retryWrites=true&w=majority"
        self.mongo_client = None
        self.mongo_db = None
        
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
    
    def migrate_groups(self) -> int:
        """Миграция групп через API."""
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
            
            # Здесь можно добавить API вызовы для создания групп
            # Пока просто логируем
            for group_name, group_id in groups_data.items():
                logger.info(f"  📝 Группа: {group_name} (ID: {group_id})")
                migrated_count += 1
            
            logger.info(f"✅ Найдено групп для миграции: {migrated_count}")
            return migrated_count
            
        except Exception as e:
            logger.error(f"❌ Ошибка при миграции групп: {e}")
            return 0
    
    def migrate_posts(self) -> int:
        """Миграция постов через API."""
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
                    # Здесь можно добавить API вызовы для создания постов
                    # Пока просто логируем
                    title = doc.get('title', f'Post from {collection_name}')
                    content = ' '.join(doc.get('lip', [])) if doc.get('lip') else ''
                    
                    logger.info(f"    📝 Пост: {title[:50]}...")
                    migrated_count += 1
                
                logger.info(f"  ✅ Коллекция {collection_name}: {len(documents)} постов")
            
            logger.info(f"✅ Найдено постов для миграции: {migrated_count}")
            return migrated_count
            
        except Exception as e:
            logger.error(f"❌ Ошибка при миграции постов: {e}")
            return 0
    
    def create_migration_summary(self, groups_count: int, posts_count: int):
        """Создание сводки миграции."""
        summary = {
            "migration_timestamp": datetime.now().isoformat(),
            "groups_found": groups_count,
            "posts_found": posts_count,
            "status": "ready_for_migration",
            "next_steps": [
                "1. Развернуть проект на Render.com",
                "2. Создать таблицы PostgreSQL",
                "3. Запустить миграцию через API",
                "4. Проверить данные в веб-интерфейсе"
            ]
        }
        
        with open("migration_summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info("📄 Сводка миграции сохранена в migration_summary.json")
        return summary
    
    def run_analysis(self) -> Dict[str, Any]:
        """Запуск анализа для миграции."""
        logger.info("🚀 Запускаем анализ для автоматической миграции...")
        
        if not self.connect_mongo():
            raise Exception("Не удалось подключиться к MongoDB")
        
        # Анализируем данные
        groups_count = self.migrate_groups()
        posts_count = self.migrate_posts()
        
        # Создаем сводку
        summary = self.create_migration_summary(groups_count, posts_count)
        
        # Закрываем соединение
        if self.mongo_client:
            self.mongo_client.close()
        
        logger.info("✅ Анализ завершен!")
        return summary

def main():
    """Главная функция."""
    print("🤖 Автоматический анализ для миграции данных")
    print("=" * 60)
    
    try:
        # Создаем мигратор
        migrator = AutoMigrator()
        
        # Запускаем анализ
        results = migrator.run_analysis()
        
        # Выводим результаты
        print("\n📊 РЕЗУЛЬТАТЫ АНАЛИЗА:")
        print("-" * 40)
        print(f"👥 Групп найдено: {results['groups_found']}")
        print(f"📝 Постов найдено: {results['posts_found']}")
        print(f"📄 Статус: {results['status']}")
        
        print("\n📋 СЛЕДУЮЩИЕ ШАГИ:")
        for step in results['next_steps']:
            print(f"  {step}")
        
        print(f"\n📄 Подробная сводка: migration_summary.json")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при анализе: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
