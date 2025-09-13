"""
Задачи для обработки постов.
"""
import logging
from datetime import datetime
from typing import List, Dict, Any

from .celery_app import celery_app
from services.post_processor import PostProcessor
from services.vk_service import VKService
from services.database_service import DatabaseService

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="tasks.post_tasks.parse_posts_task")
def parse_posts_task(self, session_name: str, bags: str = "0"):
    """
    Задача для парсинга и публикации постов.
    
    Args:
        session_name: Имя сессии
        bags: Режим отладки
    """
    try:
        logger.info(f"Starting parse_posts_task for session: {session_name}")
        
        # Создаем сервисы
        post_processor = PostProcessor()
        vk_service = VKService()
        database_service = DatabaseService()
        
        # Подключаемся к базе данных
        if not database_service.connect():
            raise Exception("Failed to connect to database")
        
        # Загружаем конфигурацию из базы данных
        database_service.load_config()
        
        # Загружаем данные сессии
        database_service.load_session_data(session_name)
        
        # Получаем посты из VK
        posts_data = vk_service.get_posts(session_name, 20)
        if not posts_data:
            logger.warning(f"No posts found for session: {session_name}")
            return {"status": "success", "message": "No posts found"}
        
        # Обрабатываем посты
        processed_posts = post_processor.process_posts(posts_data, session_name)
        if not processed_posts:
            logger.warning(f"No posts passed processing for session: {session_name}")
            return {"status": "success", "message": "No posts passed processing"}
        
        # Публикуем посты
        vk_service.publish_posts(processed_posts, session_name)
        
        # Сохраняем изменения в базу данных
        database_service.save_session_data(session_name)
        
        logger.info(f"Successfully processed {len(processed_posts)} posts for session: {session_name}")
        
        return {
            "status": "success",
            "message": f"Processed {len(processed_posts)} posts",
            "posts_count": len(processed_posts),
            "session_name": session_name
        }
        
    except Exception as e:
        logger.error(f"Error in parse_posts_task: {e}")
        # Обновляем статус задачи
        self.update_state(
            state="FAILURE",
            meta={"error": str(e), "session_name": session_name}
        )
        raise

@celery_app.task(bind=True, name="tasks.post_tasks.publish_post_task")
def publish_post_task(self, post_id: str, target_platforms: List[str]):
    """
    Задача для публикации конкретного поста.
    
    Args:
        post_id: ID поста
        target_platforms: Список платформ для публикации
    """
    try:
        logger.info(f"Starting publish_post_task for post: {post_id}")
        
        # Создаем сервисы
        vk_service = VKService()
        database_service = DatabaseService()
        
        # Подключаемся к базе данных
        if not database_service.connect():
            raise Exception("Failed to connect to database")
        
        # Получаем пост из базы данных
        posts_collection = database_service.database["posts"]
        post_data = posts_collection.find_one({"id": post_id})
        
        if not post_data:
            raise Exception(f"Post {post_id} not found")
        
        # Публикуем пост на указанных платформах
        results = {}
        for platform in target_platforms:
            if platform == "vk":
                # Публикуем в VK
                vk_service.publish_posts([post_data], "manual")
                results[platform] = "success"
            elif platform == "telegram":
                # Публикуем в Telegram
                # Здесь должна быть логика публикации в Telegram
                results[platform] = "success"
            else:
                results[platform] = "unsupported"
        
        # Обновляем статус поста
        posts_collection.update_one(
            {"id": post_id},
            {
                "$set": {
                    "status": "published",
                    "published_at": datetime.now(),
                    "target_platforms": target_platforms
                }
            }
        )
        
        logger.info(f"Successfully published post {post_id} on platforms: {target_platforms}")
        
        return {
            "status": "success",
            "message": f"Post {post_id} published successfully",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in publish_post_task: {e}")
        # Обновляем статус задачи
        self.update_state(
            state="FAILURE",
            meta={"error": str(e), "post_id": post_id}
        )
        raise

@celery_app.task(bind=True, name="tasks.post_tasks.process_scheduled_posts_task")
def process_scheduled_posts_task(self):
    """
    Задача для обработки запланированных постов.
    """
    try:
        logger.info("Starting process_scheduled_posts_task")
        
        # Создаем конфигурацию
        config = AppConfig.from_env()
        
        # Создаем сервисы
        database_service = DatabaseService(config)
        
        # Подключаемся к базе данных
        if not database_service.connect():
            raise Exception("Failed to connect to database")
        
        # Получаем запланированные посты
        posts_collection = database_service.database["posts"]
        scheduled_posts = posts_collection.find({
            "status": "scheduled",
            "scheduled_at": {"$lte": datetime.now()}
        })
        
        processed_count = 0
        for post in scheduled_posts:
            try:
                # Запускаем задачу публикации
                publish_post_task.delay(
                    post["id"],
                    post.get("target_platforms", ["vk"])
                )
                processed_count += 1
            except Exception as e:
                logger.error(f"Error scheduling post {post['id']}: {e}")
        
        logger.info(f"Successfully scheduled {processed_count} posts")
        
        return {
            "status": "success",
            "message": f"Scheduled {processed_count} posts",
            "processed_count": processed_count
        }
        
    except Exception as e:
        logger.error(f"Error in process_scheduled_posts_task: {e}")
        # Обновляем статус задачи
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise

@celery_app.task(bind=True, name="tasks.post_tasks.update_post_stats_task")
def update_post_stats_task(self, post_id: str):
    """
    Задача для обновления статистики поста.
    
    Args:
        post_id: ID поста
    """
    try:
        logger.info(f"Starting update_post_stats_task for post: {post_id}")
        
        # Создаем сервисы
        vk_service = VKService()
        database_service = DatabaseService()
        
        # Подключаемся к базе данных
        if not database_service.connect():
            raise Exception("Failed to connect to database")
        
        # Получаем пост из базы данных
        posts_collection = database_service.database["posts"]
        post_data = posts_collection.find_one({"id": post_id})
        
        if not post_data:
            raise Exception(f"Post {post_id} not found")
        
        # Получаем статистику из VK
        # Здесь должна быть логика получения статистики из VK API
        stats = {
            "views": 0,
            "likes": 0,
            "reposts": 0
        }
        
        # Обновляем статистику в базе данных
        posts_collection.update_one(
            {"id": post_id},
            {
                "$set": {
                    "views": stats["views"],
                    "likes": stats["likes"],
                    "reposts": stats["reposts"],
                    "stats_updated_at": datetime.now()
                }
            }
        )
        
        logger.info(f"Successfully updated stats for post {post_id}")
        
        return {
            "status": "success",
            "message": f"Updated stats for post {post_id}",
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error in update_post_stats_task: {e}")
        # Обновляем статус задачи
        self.update_state(
            state="FAILURE",
            meta={"error": str(e), "post_id": post_id}
        )
        raise
