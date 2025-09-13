"""
Настройка Celery для фоновых задач.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Создаем экземпляр Celery
celery_app = Celery(
    "postopus",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    include=["src.tasks.post_tasks", "src.tasks.scheduler_tasks"]
)

# Настройки Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
    result_expires=3600,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут
    task_soft_time_limit=25 * 60,  # 25 минут
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Периодические задачи
celery_app.conf.beat_schedule = {
    # Задача каждые 30 минут
    "parse-posts-every-30-minutes": {
        "task": "src.tasks.post_tasks.parse_posts_task",
        "schedule": crontab(minute="*/30"),
        "args": ("novost",)
    },
    
    # Задача каждый час
    "parse-posts-every-hour": {
        "task": "src.tasks.post_tasks.parse_posts_task",
        "schedule": crontab(minute=0),
        "args": ("reklama",)
    },
    
    # Задача каждый день в 9:00
    "daily-posts-9am": {
        "task": "src.tasks.post_tasks.parse_posts_task",
        "schedule": crontab(hour=9, minute=0),
        "args": ("sosed",)
    },
    
    # Задача каждый день в 18:00
    "daily-posts-6pm": {
        "task": "src.tasks.post_tasks.parse_posts_task",
        "schedule": crontab(hour=18, minute=0),
        "args": ("kultura",)
    },
    
    # Очистка логов каждую неделю
    "cleanup-logs-weekly": {
        "task": "src.tasks.scheduler_tasks.cleanup_logs_task",
        "schedule": crontab(hour=2, minute=0, day_of_week=1),  # Понедельник в 2:00
    },
    
    # Резервное копирование каждый день в 3:00
    "backup-daily": {
        "task": "src.tasks.scheduler_tasks.backup_database_task",
        "schedule": crontab(hour=3, minute=0),
    },
}

# Настройки для мониторинга
celery_app.conf.update(
    worker_send_task_events=True,
    task_send_sent_event=True,
)

if __name__ == "__main__":
    celery_app.start()
