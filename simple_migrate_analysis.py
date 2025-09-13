#!/usr/bin/env python3
"""
Упрощенный анализ и экспорт данных из MongoDB для последующей миграции.
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

class SimpleMongoAnalyzer:
    """Упрощенный анализатор MongoDB."""
    
    def __init__(self, mongo_url: str):
        self.mongo_url = mongo_url
        self.client = None
        self.db = None
        
    def connect(self) -> bool:
        """Подключение к MongoDB."""
        try:
            self.client = MongoClient(self.mongo_url)
            self.db = self.client['postopus']
            self.client.admin.command('ping')
            logger.info("✅ Подключение к MongoDB успешно")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к MongoDB: {e}")
            return False
    
    def analyze_and_export(self) -> Dict[str, Any]:
        """Анализ и экспорт данных."""
        logger.info("🔍 Анализируем и экспортируем данные...")
        
        if not self.connect():
            raise Exception("Не удалось подключиться к MongoDB")
        
        # Получаем все коллекции
        collections = self.db.list_collection_names()
        logger.info(f"📋 Найдено коллекций: {len(collections)}")
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "database_name": "postopus",
            "analysis": {},
            "data": {}
        }
        
        # Анализируем каждую коллекцию
        for collection_name in collections:
            logger.info(f"📄 Анализируем коллекцию: {collection_name}")
            
            collection = self.db[collection_name]
            documents = list(collection.find({}))
            
            # Анализ структуры
            analysis = self._analyze_collection(documents, collection_name)
            export_data["analysis"][collection_name] = analysis
            
            # Экспорт данных
            export_data["data"][collection_name] = documents
            
            logger.info(f"  📊 Документов: {len(documents)}")
            logger.info(f"  🔑 Поля: {list(analysis['fields'].keys())}")
        
        # Создаем план миграции
        migration_plan = self._create_migration_plan(export_data["analysis"])
        export_data["migration_plan"] = migration_plan
        
        # Сохраняем данные
        self._save_export_data(export_data)
        
        # Закрываем соединение
        if self.client:
            self.client.close()
        
        return export_data
    
    def _analyze_collection(self, documents: List[Dict], collection_name: str) -> Dict[str, Any]:
        """Анализ коллекции."""
        if not documents:
            return {"fields": {}, "document_count": 0, "is_empty": True}
        
        # Анализ полей
        field_analysis = {}
        for doc in documents:
            for field, value in doc.items():
                if field not in field_analysis:
                    field_analysis[field] = {
                        "type": type(value).__name__,
                        "count": 0,
                        "sample_values": []
                    }
                
                field_analysis[field]["count"] += 1
                
                # Сохраняем примеры значений
                if len(field_analysis[field]["sample_values"]) < 3:
                    if isinstance(value, (str, int, float, bool)):
                        field_analysis[field]["sample_values"].append(value)
                    elif isinstance(value, list) and len(value) < 5:
                        field_analysis[field]["sample_values"].append(value)
        
        return {
            "fields": field_analysis,
            "document_count": len(documents),
            "is_empty": len(documents) == 0
        }
    
    def _create_migration_plan(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Создание плана миграции."""
        plan = {
            "priority_collections": [],
            "data_mapping": {},
            "recommendations": [],
            "estimated_workload": {}
        }
        
        # Определяем приоритетные коллекции
        for collection_name, data in analysis.items():
            if data["document_count"] > 0:
                if collection_name == "config":
                    plan["priority_collections"].append({
                        "name": collection_name,
                        "priority": "high",
                        "reason": "Конфигурационные данные"
                    })
                elif collection_name not in ["logs", "statistics", "health_checks"]:
                    plan["priority_collections"].append({
                        "name": collection_name,
                        "priority": "medium",
                        "reason": "Пользовательские данные"
                    })
        
        # Планируем маппинг данных
        plan["data_mapping"] = {
            "posts": {
                "source_collections": [col for col in analysis.keys() if col not in ["users", "config", "logs", "statistics", "health_checks", "task_executions", "tasks", "deserter", "bal"]],
                "target_table": "posts",
                "strategy": "merge_all_collections"
            },
            "groups": {
                "source_collections": ["config"],
                "target_table": "groups",
                "strategy": "extract_from_config"
            },
            "users": {
                "source_collections": ["users"],
                "target_table": "users",
                "strategy": "direct_mapping"
            },
            "schedules": {
                "source_collections": ["tasks"],
                "target_table": "schedules",
                "strategy": "direct_mapping"
            }
        }
        
        # Рекомендации
        plan["recommendations"] = [
            "Создать резервную копию MongoDB перед миграцией",
            "Протестировать миграцию на копии данных",
            "Добавить поле source_collection в таблицу posts",
            "Создать индексы для часто используемых полей",
            "Настроить автоматическое создание пользователя admin"
        ]
        
        return plan
    
    def _save_export_data(self, data: Dict[str, Any]):
        """Сохранение экспортированных данных."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Полный экспорт
        full_export_file = f"mongo_full_export_{timestamp}.json"
        with open(full_export_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        # Экспорт только данных (без анализа)
        data_only_file = f"mongo_data_only_{timestamp}.json"
        with open(data_only_file, 'w', encoding='utf-8') as f:
            json.dump(data["data"], f, ensure_ascii=False, indent=2, default=str)
        
        # Экспорт плана миграции
        plan_file = f"migration_plan_{timestamp}.json"
        with open(plan_file, 'w', encoding='utf-8') as f:
            json.dump(data["migration_plan"], f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"✅ Данные экспортированы:")
        logger.info(f"  📄 Полный экспорт: {full_export_file}")
        logger.info(f"  📄 Только данные: {data_only_file}")
        logger.info(f"  📄 План миграции: {plan_file}")

def main():
    """Главная функция."""
    print("🔍 Упрощенный анализ и экспорт данных MongoDB")
    print("=" * 60)
    
    # URL MongoDB
    mongo_url = "mongodb+srv://valstan:nitro2000@postopus.qjxr9.mongodb.net/postopus?retryWrites=true&w=majority"
    
    try:
        # Создаем анализатор
        analyzer = SimpleMongoAnalyzer(mongo_url)
        
        # Запускаем анализ и экспорт
        results = analyzer.analyze_and_export()
        
        # Выводим краткую сводку
        print("\n📊 КРАТКАЯ СВОДКА:")
        print("-" * 40)
        
        analysis = results.get('analysis', {})
        print(f"📋 Коллекций проанализировано: {len(analysis)}")
        
        total_docs = sum(data['document_count'] for data in analysis.values())
        print(f"📄 Всего документов: {total_docs}")
        
        # Статистика по типам коллекций
        post_collections = [col for col in analysis.keys() if col not in ['users', 'config', 'logs', 'statistics', 'health_checks', 'task_executions', 'tasks', 'deserter', 'bal']]
        print(f"📝 Коллекций с постами: {len(post_collections)}")
        
        config_data = analysis.get('config', {})
        if config_data and not config_data.get('is_empty', True):
            print(f"⚙️ Конфигурация найдена")
        
        users_data = analysis.get('users', {})
        print(f"👤 Пользователей: {users_data.get('document_count', 0)}")
        
        tasks_data = analysis.get('tasks', {})
        print(f"⏰ Задач: {tasks_data.get('document_count', 0)}")
        
        print(f"\n📄 Файлы экспорта созданы в текущей директории")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при анализе: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
