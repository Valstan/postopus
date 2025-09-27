"""
Simplified Celery tasks for production deployment.
These tasks avoid async/await issues and work with the deployment environment.
"""
import logging
from datetime import datetime
from typing import List, Dict, Any

from .celery_app import celery_app

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="tasks.simple_tasks.demo_task")
def demo_task(self, message: str = "Hello from Celery!"):
    """
    Simple demo task for testing Celery functionality.
    
    Args:
        message: Message to log
    """
    try:
        logger.info(f"Demo task executing: {message}")
        
        # Simulate some work
        import time
        time.sleep(2)
        
        result = {
            "status": "success",
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "task_id": self.request.id
        }
        
        logger.info(f"Demo task completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in demo_task: {e}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e), "message": message}
        )
        raise

@celery_app.task(bind=True, name="tasks.simple_tasks.health_check_task")
def health_check_task(self):
    """
    Health check task for monitoring.
    """
    try:
        logger.info("Health check task executing")
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "celery_worker": "operational",
            "task_id": self.request.id
        }
        
    except Exception as e:
        logger.error(f"Error in health_check_task: {e}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise

@celery_app.task(bind=True, name="tasks.simple_tasks.process_statistics_task")
def process_statistics_task(self):
    """
    Process statistics task (demo version).
    """
    try:
        logger.info("Processing statistics task")
        
        # Demo statistics processing
        stats = {
            "total_posts": 1547,
            "processed_today": 23,
            "active_sessions": 15,
            "error_count": 2,
            "last_update": datetime.now().isoformat()
        }
        
        logger.info(f"Statistics processed: {stats}")
        
        return {
            "status": "success",
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in process_statistics_task: {e}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise

# Optional: Periodic tasks (can be enabled later)
from celery.schedules import crontab

# Uncomment to enable periodic tasks
# celery_app.conf.beat_schedule = {
#     'health-check-every-5-minutes': {
#         'task': 'tasks.simple_tasks.health_check_task',
#         'schedule': crontab(minute='*/5'),
#     },
#     'process-statistics-every-hour': {
#         'task': 'tasks.simple_tasks.process_statistics_task',
#         'schedule': crontab(minute=0),
#     },
# }