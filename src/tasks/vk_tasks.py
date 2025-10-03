"""
Modern Celery tasks for VK API integration in Postopus
"""
import logging
from datetime import datetime
from typing import List, Dict, Any
import asyncio

from .celery_app import celery_app
from ..services.modern_vk_service import ModernVKService
from ..web.database import get_database
from ..web.models import Post, Group, VKToken

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="tasks.vk_tasks.fetch_posts_from_region")
def fetch_posts_from_region_task(self, region: str, count: int = 20):
    """
    Задача для получения постов из VK групп региона.
    
    Args:
        region: Регион для получения постов
        count: Количество постов для получения
    """
    try:
        logger.info(f"Starting fetch_posts_from_region_task for region: {region}")
        
        # Создаем VK сервис
        vk_service = ModernVKService()
        
        # Инициализируем сервис
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            initialized = loop.run_until_complete(vk_service.initialize())
            if not initialized:
                raise Exception("Failed to initialize VK service")
            
            # Получаем посты
            posts = loop.run_until_complete(vk_service.get_posts_by_region(region, count))
            
            if not posts:
                logger.warning(f"No posts found for region: {region}")
                return {"status": "success", "message": "No posts found", "posts_count": 0}
            
            # Сохраняем посты в базу данных
            saved_count = 0
            for post_data in posts:
                post_id = loop.run_until_complete(vk_service.save_post_to_db(post_data))
                if post_id:
                    saved_count += 1
            
            logger.info(f"Successfully fetched and saved {saved_count} posts for region {region}")
            
            return {
                "status": "success",
                "message": f"Fetched and saved {saved_count} posts",
                "posts_count": saved_count,
                "region": region
            }
            
        finally:
            loop.close()
        
    except Exception as e:
        logger.error(f"Error in fetch_posts_from_region_task: {e}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e), "region": region}
        )
        raise


@celery_app.task(bind=True, name="tasks.vk_tasks.publish_post_to_vk")
def publish_post_to_vk_task(self, post_id: int, target_groups: List[str] = None, region: str = None):
    """
    Задача для публикации поста в VK группы.
    
    Args:
        post_id: ID поста в базе данных
        target_groups: Список групп для публикации
        region: Регион для публикации
    """
    try:
        logger.info(f"Starting publish_post_to_vk_task for post: {post_id}")
        
        # Получаем пост из базы данных
        db = get_database()
        with db.get_session() as session:
            post = session.query(Post).filter(Post.id == post_id).first()
            if not post:
                raise Exception(f"Post {post_id} not found")
            
            post_data = {
                'id': post.id,
                'text': post.content,
                'title': post.title,
                'theme': post.theme,
                'region': post.region
            }
        
        # Создаем VK сервис
        vk_service = ModernVKService()
        
        # Инициализируем сервис
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            initialized = loop.run_until_complete(vk_service.initialize())
            if not initialized:
                raise Exception("Failed to initialize VK service")
            
            # Если группы не указаны, получаем группы региона
            if not target_groups:
                if not region:
                    region = post.region
                
                groups = loop.run_until_complete(vk_service._get_groups_by_region(region))
                target_groups = [group.group_id for group in groups]
            
            if not target_groups:
                raise Exception("No target groups specified")
            
            # Публикуем пост
            results = loop.run_until_complete(
                vk_service.publish_to_groups(post_data, target_groups, region)
            )
            
            # Обновляем статус поста
            if results['success']:
                loop.run_until_complete(
                    vk_service.update_post_status(post_id, 'published')
                )
                logger.info(f"Successfully published post {post_id} to {len(results['success'])} groups")
            else:
                loop.run_until_complete(
                    vk_service.update_post_status(post_id, 'error')
                )
                logger.error(f"Failed to publish post {post_id} to any groups")
            
            return {
                "status": "success",
                "message": f"Published to {len(results['success'])}/{len(target_groups)} groups",
                "results": results,
                "post_id": post_id
            }
            
        finally:
            loop.close()
        
    except Exception as e:
        logger.error(f"Error in publish_post_to_vk_task: {e}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e), "post_id": post_id}
        )
        raise


@celery_app.task(bind=True, name="tasks.vk_tasks.test_vk_connections")
def test_vk_connections_task(self):
    """
    Задача для тестирования подключений к VK API.
    """
    try:
        logger.info("Starting test_vk_connections_task")
        
        # Создаем VK сервис
        vk_service = ModernVKService()
        
        # Инициализируем сервис
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            initialized = loop.run_until_complete(vk_service.initialize())
            if not initialized:
                raise Exception("Failed to initialize VK service")
            
            # Тестируем подключения
            results = loop.run_until_complete(vk_service.test_connection())
            
            logger.info(f"VK connections test completed: {results['working_tokens']}/{results['total_tokens']} working")
            
            return {
                "status": "success",
                "message": f"Tested {results['total_tokens']} tokens, {results['working_tokens']} working",
                "results": results
            }
            
        finally:
            loop.close()
        
    except Exception as e:
        logger.error(f"Error in test_vk_connections_task: {e}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise


@celery_app.task(bind=True, name="tasks.vk_tasks.process_scheduled_posts")
def process_scheduled_posts_task(self):
    """
    Задача для обработки запланированных постов.
    """
    try:
        logger.info("Starting process_scheduled_posts_task")
        
        # Получаем запланированные посты
        db = get_database()
        with db.get_session() as session:
            scheduled_posts = session.query(Post).filter(
                Post.status == 'scheduled',
                Post.scheduled_at <= datetime.utcnow()
            ).all()
        
        if not scheduled_posts:
            logger.info("No scheduled posts found")
            return {"status": "success", "message": "No scheduled posts found", "processed_count": 0}
        
        processed_count = 0
        for post in scheduled_posts:
            try:
                # Запускаем задачу публикации
                publish_post_to_vk_task.delay(post.id, region=post.region)
                processed_count += 1
                logger.info(f"Scheduled post {post.id} for publishing")
            except Exception as e:
                logger.error(f"Error scheduling post {post.id}: {e}")
        
        logger.info(f"Successfully scheduled {processed_count} posts for publishing")
        
        return {
            "status": "success",
            "message": f"Scheduled {processed_count} posts",
            "processed_count": processed_count
        }
        
    except Exception as e:
        logger.error(f"Error in process_scheduled_posts_task: {e}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise


@celery_app.task(bind=True, name="tasks.vk_tasks.update_post_statistics")
def update_post_statistics_task(self, post_id: int):
    """
    Задача для обновления статистики поста из VK.
    
    Args:
        post_id: ID поста в базе данных
    """
    try:
        logger.info(f"Starting update_post_statistics_task for post: {post_id}")
        
        # Получаем пост из базы данных
        db = get_database()
        with db.get_session() as session:
            post = session.query(Post).filter(Post.id == post_id).first()
            if not post:
                raise Exception(f"Post {post_id} not found")
            
            if not post.vk_post_id or not post.vk_group_id:
                raise Exception(f"Post {post_id} has no VK post ID or group ID")
        
        # Создаем VK сервис
        vk_service = ModernVKService()
        
        # Инициализируем сервис
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            initialized = loop.run_until_complete(vk_service.initialize())
            if not initialized:
                raise Exception("Failed to initialize VK service")
            
            # Получаем статистику поста из VK
            # Здесь должна быть логика получения статистики из VK API
            # Пока используем заглушку
            stats = {
                "views": 0,
                "likes": 0,
                "reposts": 0,
                "comments": 0
            }
            
            # Обновляем статистику в базе данных
            with db.get_session() as session:
                post = session.query(Post).filter(Post.id == post_id).first()
                if post:
                    post.views = stats["views"]
                    post.likes = stats["likes"]
                    post.reposts = stats["reposts"]
                    post.comments = stats["comments"]
                    post.stats_updated_at = datetime.utcnow()
                    session.commit()
            
            logger.info(f"Successfully updated statistics for post {post_id}")
            
            return {
                "status": "success",
                "message": f"Updated statistics for post {post_id}",
                "stats": stats,
                "post_id": post_id
            }
            
        finally:
            loop.close()
        
    except Exception as e:
        logger.error(f"Error in update_post_statistics_task: {e}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e), "post_id": post_id}
        )
        raise


@celery_app.task(bind=True, name="tasks.vk_tasks.sync_all_regions")
def sync_all_regions_task(self):
    """
    Задача для синхронизации постов из всех регионов.
    """
    try:
        logger.info("Starting sync_all_regions_task")
        
        # Получаем все активные регионы
        db = get_database()
        with db.get_session() as session:
            regions = session.query(VKToken.region).filter(VKToken.is_active == True).distinct().all()
        
        if not regions:
            logger.warning("No active regions found")
            return {"status": "success", "message": "No active regions found", "processed_regions": 0}
        
        processed_regions = 0
        for (region,) in regions:
            try:
                # Запускаем задачу получения постов для региона
                fetch_posts_from_region_task.delay(region, 20)
                processed_regions += 1
                logger.info(f"Scheduled sync for region: {region}")
            except Exception as e:
                logger.error(f"Error scheduling sync for region {region}: {e}")
        
        logger.info(f"Successfully scheduled sync for {processed_regions} regions")
        
        return {
            "status": "success",
            "message": f"Scheduled sync for {processed_regions} regions",
            "processed_regions": processed_regions
        }
        
    except Exception as e:
        logger.error(f"Error in sync_all_regions_task: {e}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise
