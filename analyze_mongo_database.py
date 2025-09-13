#!/usr/bin/env python3
"""
Скрипт для анализа структуры и содержимого MongoDB базы данных PostOpus.
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Set
from collections import Counter, defaultdict
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MongoAnalyzer:
    """Класс для анализа MongoDB базы данных."""
    
    def __init__(self, mongo_url: str):
        self.mongo_url = mongo_url
        self.client = None
        self.db = None
        self.analysis_results = {}
        
    def connect(self) -> bool:
        """Подключение к MongoDB."""
        try:
            self.client = MongoClient(self.mongo_url)
            self.db = self.client['postopus']
            
            # Тестируем соединение
            self.client.admin.command('ping')
            logger.info("✅ Подключение к MongoDB успешно")
            return True
        except ConnectionFailure as e:
            logger.error(f"❌ Ошибка подключения к MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка при подключении: {e}")
            return False
    
    def analyze_collections(self) -> Dict[str, Any]:
        """Анализ коллекций в базе данных."""
        logger.info("🔍 Анализируем коллекции...")
        
        collections = self.db.list_collection_names()
        logger.info(f"📋 Найдено коллекций: {len(collections)}")
        
        collection_analysis = {}
        
        for collection_name in collections:
            logger.info(f"📄 Анализируем коллекцию: {collection_name}")
            
            collection = self.db[collection_name]
            
            # Основная информация о коллекции
            doc_count = collection.count_documents({})
            
            # Анализ структуры документов
            sample_docs = list(collection.find().limit(10))
            field_analysis = self._analyze_document_structure(sample_docs)
            
            # Анализ индексов
            indexes = list(collection.list_indexes())
            
            collection_analysis[collection_name] = {
                'document_count': doc_count,
                'sample_documents': sample_docs,
                'field_analysis': field_analysis,
                'indexes': indexes,
                'is_empty': doc_count == 0
            }
            
            logger.info(f"  📊 Документов: {doc_count}")
            logger.info(f"  🔑 Поля: {list(field_analysis.keys())}")
        
        return collection_analysis
    
    def _analyze_document_structure(self, documents: List[Dict]) -> Dict[str, Any]:
        """Анализ структуры документов."""
        if not documents:
            return {}
        
        field_types = defaultdict(set)
        field_values = defaultdict(list)
        field_counts = defaultdict(int)
        
        for doc in documents:
            for field, value in doc.items():
                field_types[field].add(type(value).__name__)
                field_counts[field] += 1
                
                # Сохраняем примеры значений (только для небольших данных)
                if isinstance(value, (str, int, float, bool)) and len(str(value)) < 100:
                    field_values[field].append(value)
                elif isinstance(value, dict) and len(str(value)) < 200:
                    field_values[field].append(value)
                elif isinstance(value, list) and len(value) < 10:
                    field_values[field].append(value)
        
        # Анализируем типы полей
        field_analysis = {}
        for field, types in field_types.items():
            field_analysis[field] = {
                'types': list(types),
                'count': field_counts[field],
                'sample_values': field_values[field][:5],  # Первые 5 примеров
                'is_optional': field_counts[field] < len(documents)
            }
        
        return field_analysis
    
    def analyze_posts_data(self) -> Dict[str, Any]:
        """Специальный анализ данных постов."""
        logger.info("📝 Анализируем данные постов...")
        
        posts_analysis = {
            'collections_with_posts': [],
            'total_posts': 0,
            'post_types': Counter(),
            'platforms': Counter(),
            'statuses': Counter(),
            'date_ranges': {},
            'content_analysis': {}
        }
        
        # Ищем коллекции с постами
        collections = self.db.list_collection_names()
        post_collections = [col for col in collections if col not in [
            'users', 'settings', 'logs', 'statistics', 'health_checks', 
            'task_executions', 'tasks', 'config', 'deserter', 'bal'
        ]]
        
        posts_analysis['collections_with_posts'] = post_collections
        
        for collection_name in post_collections:
            collection = self.db[collection_name]
            doc_count = collection.count_documents({})
            posts_analysis['total_posts'] += doc_count
            
            logger.info(f"  📄 {collection_name}: {doc_count} постов")
            
            # Анализируем структуру постов
            sample_posts = list(collection.find().limit(50))
            
            for post in sample_posts:
                # Анализируем типы контента
                if 'image' in post or 'image_url' in post:
                    posts_analysis['post_types']['with_image'] += 1
                if 'video' in post or 'video_url' in post:
                    posts_analysis['post_types']['with_video'] += 1
                if 'text' in post or 'content' in post:
                    posts_analysis['post_types']['with_text'] += 1
                
                # Анализируем платформы
                if 'vk_group_id' in post or 'group_id' in post:
                    posts_analysis['platforms']['vk'] += 1
                if 'telegram_chat_id' in post:
                    posts_analysis['platforms']['telegram'] += 1
                
                # Анализируем статусы
                status = post.get('status', 'unknown')
                posts_analysis['statuses'][status] += 1
                
                # Анализируем даты
                created_at = post.get('created_at')
                if created_at:
                    if collection_name not in posts_analysis['date_ranges']:
                        posts_analysis['date_ranges'][collection_name] = {
                            'earliest': created_at,
                            'latest': created_at
                        }
                    else:
                        if created_at < posts_analysis['date_ranges'][collection_name]['earliest']:
                            posts_analysis['date_ranges'][collection_name]['earliest'] = created_at
                        if created_at > posts_analysis['date_ranges'][collection_name]['latest']:
                            posts_analysis['date_ranges'][collection_name]['latest'] = created_at
        
        return posts_analysis
    
    def analyze_config_data(self) -> Dict[str, Any]:
        """Анализ конфигурационных данных."""
        logger.info("⚙️ Анализируем конфигурационные данные...")
        
        config_analysis = {
            'config_documents': {},
            'groups': {},
            'users': {},
            'tasks': {},
            'settings': {}
        }
        
        # Анализируем коллекцию config
        config_collection = self.db['config']
        config_docs = list(config_collection.find({}))
        
        for doc in config_docs:
            doc_title = doc.get('title', 'unknown')
            config_analysis['config_documents'][doc_title] = {
                'keys': list(doc.keys()),
                'has_groups': 'all_my_groups' in doc,
                'has_filters': any(key in doc for key in ['delete_msg_blacklist', 'clear_text_blacklist', 'black_id']),
                'document_size': len(str(doc))
            }
            
            # Анализируем группы
            if 'all_my_groups' in doc:
                groups = doc['all_my_groups']
                config_analysis['groups'] = {
                    'count': len(groups),
                    'groups': groups,
                    'platforms': list(set(str(gid)[0] if str(gid).startswith('-') else 'positive' for gid in groups.values()))
                }
        
        # Анализируем пользователей
        users_collection = self.db['users']
        users = list(users_collection.find({}))
        config_analysis['users'] = {
            'count': len(users),
            'users': [{'username': u.get('username'), 'email': u.get('email'), 'is_admin': u.get('is_admin', False)} for u in users]
        }
        
        # Анализируем задачи
        tasks_collection = self.db['tasks']
        tasks = list(tasks_collection.find({}))
        config_analysis['tasks'] = {
            'count': len(tasks),
            'enabled_tasks': len([t for t in tasks if t.get('enabled', False)]),
            'task_types': list(set(t.get('type', 'unknown') for t in tasks))
        }
        
        return config_analysis
    
    def generate_migration_plan(self) -> Dict[str, Any]:
        """Генерация плана миграции на основе анализа."""
        logger.info("📋 Генерируем план миграции...")
        
        migration_plan = {
            'priority_collections': [],
            'data_mapping': {},
            'recommendations': [],
            'potential_issues': [],
            'estimated_workload': {}
        }
        
        # Определяем приоритетные коллекции
        collections = self.analysis_results.get('collections', {})
        
        for collection_name, analysis in collections.items():
            if analysis['document_count'] > 0:
                if collection_name in ['users', 'config']:
                    migration_plan['priority_collections'].append({
                        'name': collection_name,
                        'priority': 'high',
                        'reason': 'Критически важные данные'
                    })
                elif collection_name not in ['logs', 'statistics', 'health_checks']:
                    migration_plan['priority_collections'].append({
                        'name': collection_name,
                        'priority': 'medium',
                        'reason': 'Пользовательские данные'
                    })
        
        # Планируем маппинг данных
        migration_plan['data_mapping'] = {
            'posts': {
                'source_collections': [col for col in collections.keys() if col not in ['users', 'config', 'logs', 'statistics', 'health_checks', 'task_executions', 'tasks', 'deserter', 'bal']],
                'target_table': 'posts',
                'strategy': 'merge_all_collections'
            },
            'groups': {
                'source_collections': ['config'],
                'target_table': 'groups',
                'strategy': 'extract_from_config'
            },
            'users': {
                'source_collections': ['users'],
                'target_table': 'users',
                'strategy': 'direct_mapping'
            },
            'schedules': {
                'source_collections': ['tasks'],
                'target_table': 'schedules',
                'strategy': 'direct_mapping'
            }
        }
        
        # Рекомендации
        migration_plan['recommendations'] = [
            "Создать резервную копию MongoDB перед миграцией",
            "Протестировать миграцию на копии данных",
            "Добавить поле source_collection в таблицу posts для отслеживания источника",
            "Создать индексы для часто используемых полей",
            "Настроить автоматическое создание пользователя admin если пользователей нет"
        ]
        
        return migration_plan
    
    def save_analysis_report(self, output_file: str = "mongo_analysis_report.json"):
        """Сохранение отчета анализа."""
        logger.info(f"💾 Сохраняем отчет анализа в {output_file}")
        
        report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'database_url': self.mongo_url.replace(self.mongo_url.split('@')[0].split('//')[1].split(':')[0], '***'),
            'analysis_results': self.analysis_results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"✅ Отчет сохранен: {output_file}")
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """Запуск полного анализа базы данных."""
        logger.info("🚀 Начинаем полный анализ MongoDB базы данных...")
        
        if not self.connect():
            raise Exception("Не удалось подключиться к MongoDB")
        
        # Анализируем коллекции
        self.analysis_results['collections'] = self.analyze_collections()
        
        # Анализируем посты
        self.analysis_results['posts_analysis'] = self.analyze_posts_data()
        
        # Анализируем конфигурацию
        self.analysis_results['config_analysis'] = self.analyze_config_data()
        
        # Генерируем план миграции
        self.analysis_results['migration_plan'] = self.generate_migration_plan()
        
        # Сохраняем отчет
        self.save_analysis_report()
        
        # Закрываем соединение
        if self.client:
            self.client.close()
        
        logger.info("✅ Анализ завершен!")
        return self.analysis_results

def main():
    """Главная функция."""
    print("🔍 Анализатор MongoDB базы данных PostOpus")
    print("=" * 60)
    
    # URL MongoDB
    mongo_url = "mongodb+srv://valstan:nitro2000@postopus.qjxr9.mongodb.net/postopus?retryWrites=true&w=majority"
    
    try:
        # Создаем анализатор
        analyzer = MongoAnalyzer(mongo_url)
        
        # Запускаем анализ
        results = analyzer.run_full_analysis()
        
        # Выводим краткую сводку
        print("\n📊 КРАТКАЯ СВОДКА АНАЛИЗА:")
        print("-" * 40)
        
        collections = results.get('collections', {})
        print(f"📋 Коллекций найдено: {len(collections)}")
        
        total_docs = sum(col['document_count'] for col in collections.values())
        print(f"📄 Всего документов: {total_docs}")
        
        posts_analysis = results.get('posts_analysis', {})
        print(f"📝 Постов найдено: {posts_analysis.get('total_posts', 0)}")
        print(f"📂 Коллекций с постами: {len(posts_analysis.get('collections_with_posts', []))}")
        
        config_analysis = results.get('config_analysis', {})
        groups = config_analysis.get('groups', {})
        print(f"👥 Групп в конфигурации: {groups.get('count', 0)}")
        
        users = config_analysis.get('users', {})
        print(f"👤 Пользователей: {users.get('count', 0)}")
        
        tasks = config_analysis.get('tasks', {})
        print(f"⏰ Задач: {tasks.get('count', 0)}")
        
        print(f"\n📄 Подробный отчет сохранен в: mongo_analysis_report.json")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при анализе: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
