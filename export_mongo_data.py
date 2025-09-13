#!/usr/bin/env python3
"""
Скрипт для экспорта данных из MongoDB в JSON файлы.
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def export_mongo_data(mongo_url: str, output_dir: str = "mongo_export"):
    """Экспорт данных из MongoDB в JSON файлы."""
    
    try:
        # Подключаемся к MongoDB
        client = MongoClient(mongo_url)
        db = client['postopus']
        
        # Тестируем соединение
        client.admin.command('ping')
        logger.info("✅ Подключение к MongoDB успешно")
        
        # Создаем директорию для экспорта
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Получаем список коллекций
        collections = db.list_collection_names()
        logger.info(f"📋 Найдено коллекций: {len(collections)}")
        
        exported_data = {
            "export_timestamp": datetime.now().isoformat(),
            "database_name": "postopus",
            "collections": {}
        }
        
        for collection_name in collections:
            logger.info(f"📄 Экспортируем коллекцию: {collection_name}")
            
            try:
                collection = db[collection_name]
                
                # Получаем все документы
                documents = list(collection.find({}))
                
                # Конвертируем ObjectId в строки
                for doc in documents:
                    if '_id' in doc:
                        doc['_id'] = str(doc['_id'])
                
                exported_data["collections"][collection_name] = documents
                logger.info(f"✅ Коллекция {collection_name}: {len(documents)} документов")
                
            except Exception as e:
                logger.error(f"❌ Ошибка при экспорте коллекции {collection_name}: {e}")
                continue
        
        # Сохраняем данные в JSON файл
        output_file = os.path.join(output_dir, f"postopus_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(exported_data, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"✅ Данные экспортированы в: {output_file}")
        
        # Создаем отдельные файлы для каждой коллекции
        for collection_name, documents in exported_data["collections"].items():
            collection_file = os.path.join(output_dir, f"{collection_name}.json")
            with open(collection_file, 'w', encoding='utf-8') as f:
                json.dump(documents, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"📄 Коллекция {collection_name} сохранена в: {collection_file}")
        
        # Закрываем соединение
        client.close()
        
        return output_file
        
    except ConnectionFailure as e:
        logger.error(f"❌ Ошибка подключения к MongoDB: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {e}")
        return None

def main():
    """Главная функция."""
    print("📤 Скрипт экспорта данных из MongoDB")
    print("=" * 50)
    
    # Получаем URL MongoDB
    mongo_url = input("Введите URL MongoDB (например: mongodb://user:pass@host:port/): ").strip()
    if not mongo_url:
        print("❌ URL MongoDB не может быть пустым")
        return
    
    # Запускаем экспорт
    result = export_mongo_data(mongo_url)
    
    if result:
        print(f"\n✅ Экспорт завершен успешно!")
        print(f"📁 Файл: {result}")
    else:
        print("\n❌ Ошибка при экспорте данных")

if __name__ == "__main__":
    main()
