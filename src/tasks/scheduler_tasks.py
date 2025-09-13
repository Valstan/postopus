"""
Задачи для планировщика.
"""
import logging
import os
import shutil
from datetime import datetime, timedelta
from typing import List, Dict, Any

from .celery_app import celery_app
from ..services.database_service import DatabaseService

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="src.tasks.scheduler_tasks.cleanup_logs_task")
def cleanup_logs_task(self, days_to_keep: int = 30):
    """
    Задача для очистки старых логов.
    
    Args:
        days_to_keep: Количество дней для хранения логов
    """
    try:
        logger.info(f"Starting cleanup_logs_task, keeping logs for {days_to_keep} days")
        
        # Создаем сервисы
        database_service = DatabaseService()
        
        # Подключаемся к базе данных
        if not database_service.connect():
            raise Exception("Failed to connect to database")
        
        # Удаляем старые логи из базы данных
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Очищаем логи задач
        tasks_collection = database_service.database["task_executions"]
        deleted_tasks = tasks_collection.delete_many({
            "started_at": {"$lt": cutoff_date}
        })
        
        # Очищаем логи приложения
        logs_collection = database_service.database["logs"]
        deleted_logs = logs_collection.delete_many({
            "timestamp": {"$lt": cutoff_date}
        })
        
        # Очищаем файлы логов
        logs_dir = "logs"
        if os.path.exists(logs_dir):
            for filename in os.listdir(logs_dir):
                file_path = os.path.join(logs_dir, filename)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_time < cutoff_date:
                        os.remove(file_path)
                        logger.info(f"Deleted old log file: {filename}")
        
        logger.info(f"Successfully cleaned up logs: {deleted_tasks.deleted_count} task executions, {deleted_logs.deleted_count} log entries")
        
        return {
            "status": "success",
            "message": f"Cleaned up logs older than {days_to_keep} days",
            "deleted_tasks": deleted_tasks.deleted_count,
            "deleted_logs": deleted_logs.deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup_logs_task: {e}")
        # Обновляем статус задачи
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise

@celery_app.task(bind=True, name="src.tasks.scheduler_tasks.backup_database_task")
def backup_database_task(self):
    """
    Задача для создания резервной копии базы данных.
    """
    try:
        logger.info("Starting backup_database_task")
        
        # Создаем сервисы
        database_service = DatabaseService()
        
        # Подключаемся к базе данных
        if not database_service.connect():
            raise Exception("Failed to connect to database")
        
        # Создаем директорию для бэкапов
        backup_dir = "backups"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Генерируем имя файла бэкапа
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"postopus_backup_{timestamp}.json"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Экспортируем данные из базы данных
        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "database_name": config.database.database_name,
            "collections": {}
        }
        
        # Получаем список коллекций
        collections = database_service.database.list_collection_names()
        
        for collection_name in collections:
            collection = database_service.database[collection_name]
            documents = list(collection.find({}, {"_id": 0}))
            backup_data["collections"][collection_name] = documents
        
        # Сохраняем бэкап
        import json
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
        
        # Удаляем старые бэкапы (оставляем только последние 7)
        backup_files = [f for f in os.listdir(backup_dir) if f.startswith("postopus_backup_")]
        backup_files.sort(reverse=True)
        
        for old_backup in backup_files[7:]:
            old_backup_path = os.path.join(backup_dir, old_backup)
            os.remove(old_backup_path)
            logger.info(f"Deleted old backup: {old_backup}")
        
        logger.info(f"Successfully created backup: {backup_filename}")
        
        return {
            "status": "success",
            "message": f"Backup created: {backup_filename}",
            "backup_path": backup_path,
            "backup_size": os.path.getsize(backup_path)
        }
        
    except Exception as e:
        logger.error(f"Error in backup_database_task: {e}")
        # Обновляем статус задачи
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise

@celery_app.task(bind=True, name="src.tasks.scheduler_tasks.health_check_task")
def health_check_task(self):
    """
    Задача для проверки здоровья системы.
    """
    try:
        logger.info("Starting health_check_task")
        
        # Создаем сервисы
        database_service = DatabaseService()
        
        # Проверяем подключение к базе данных
        db_healthy = database_service.connect()
        
        # Проверяем доступность VK API
        vk_healthy = True  # Здесь должна быть проверка VK API
        
        # Проверяем доступность Telegram API
        telegram_healthy = True  # Здесь должна быть проверка Telegram API
        
        # Проверяем свободное место на диске
        disk_usage = shutil.disk_usage(".")
        disk_free_gb = disk_usage.free / (1024**3)
        disk_healthy = disk_free_gb > 1.0  # Минимум 1 ГБ свободного места
        
        # Проверяем использование памяти
        import psutil
        memory = psutil.virtual_memory()
        memory_healthy = memory.percent < 90  # Максимум 90% использования памяти
        
        # Определяем общий статус
        overall_healthy = all([db_healthy, vk_healthy, telegram_healthy, disk_healthy, memory_healthy])
        
        health_status = {
            "overall": "healthy" if overall_healthy else "unhealthy",
            "database": "healthy" if db_healthy else "unhealthy",
            "vk_api": "healthy" if vk_healthy else "unhealthy",
            "telegram_api": "healthy" if telegram_healthy else "unhealthy",
            "disk": "healthy" if disk_healthy else "unhealthy",
            "memory": "healthy" if memory_healthy else "unhealthy",
            "disk_free_gb": round(disk_free_gb, 2),
            "memory_percent": memory.percent,
            "timestamp": datetime.now().isoformat()
        }
        
        # Сохраняем статус в базу данных
        if db_healthy:
            health_collection = database_service.database["health_checks"]
            health_collection.insert_one(health_status)
        
        logger.info(f"Health check completed: {health_status['overall']}")
        
        return {
            "status": "success",
            "message": "Health check completed",
            "health_status": health_status
        }
        
    except Exception as e:
        logger.error(f"Error in health_check_task: {e}")
        # Обновляем статус задачи
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise

@celery_app.task(bind=True, name="src.tasks.scheduler_tasks.update_statistics_task")
def update_statistics_task(self):
    """
    Задача для обновления статистики.
    """
    try:
        logger.info("Starting update_statistics_task")
        
        # Создаем сервисы
        database_service = DatabaseService()
        
        # Подключаемся к базе данных
        if not database_service.connect():
            raise Exception("Failed to connect to database")
        
        # Получаем статистику постов
        posts_collection = database_service.database["posts"]
        
        # Статистика за сегодня
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        posts_today = posts_collection.count_documents({
            "published_at": {"$gte": today}
        })
        
        # Статистика за неделю
        week_ago = datetime.now() - timedelta(days=7)
        posts_week = posts_collection.count_documents({
            "published_at": {"$gte": week_ago}
        })
        
        # Статистика за месяц
        month_ago = datetime.now() - timedelta(days=30)
        posts_month = posts_collection.count_documents({
            "published_at": {"$gte": month_ago}
        })
        
        # Общая статистика
        total_posts = posts_collection.count_documents({})
        
        # Статистика по платформам
        platform_stats = {}
        for platform in ["vk", "telegram", "instagram"]:
            platform_stats[platform] = posts_collection.count_documents({
                "target_platforms": {"$in": [platform]}
            })
        
        # Создаем объект статистики
        statistics = {
            "timestamp": datetime.now().isoformat(),
            "posts": {
                "today": posts_today,
                "week": posts_week,
                "month": posts_month,
                "total": total_posts
            },
            "platforms": platform_stats
        }
        
        # Сохраняем статистику в базу данных
        stats_collection = database_service.database["statistics"]
        stats_collection.insert_one(statistics)
        
        logger.info(f"Successfully updated statistics: {posts_today} posts today, {total_posts} total")
        
        return {
            "status": "success",
            "message": "Statistics updated successfully",
            "statistics": statistics
        }
        
    except Exception as e:
        logger.error(f"Error in update_statistics_task: {e}")
        # Обновляем статус задачи
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise

@celery_app.task(bind=True, name="src.tasks.scheduler_tasks.cleanup_temp_files_task")
def cleanup_temp_files_task(self):
    """
    Задача для очистки временных файлов.
    """
    try:
        logger.info("Starting cleanup_temp_files_task")
        
        # Очищаем временные изображения
        temp_images_dir = "temp_images"
        if os.path.exists(temp_images_dir):
            for filename in os.listdir(temp_images_dir):
                file_path = os.path.join(temp_images_dir, filename)
                if os.path.isfile(file_path):
                    # Удаляем файлы старше 1 часа
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_time < datetime.now() - timedelta(hours=1):
                        os.remove(file_path)
                        logger.info(f"Deleted temp file: {filename}")
        
        # Очищаем другие временные файлы
        temp_files = ["ai_predict.txt", "image.jpg"]
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                logger.info(f"Deleted temp file: {temp_file}")
        
        logger.info("Successfully cleaned up temporary files")
        
        return {
            "status": "success",
            "message": "Temporary files cleaned up successfully"
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup_temp_files_task: {e}")
        # Обновляем статус задачи
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise
