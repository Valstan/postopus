"""
Настройка Celery для фоновых задач (упрощенная версия).
"""
import os
from celery import Celery

# Получаем URL Redis из переменных окружения
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
broker_url = os.environ.get('CELERY_BROKER_URL', redis_url)
result_backend = os.environ.get('CELERY_RESULT_BACKEND', redis_url)

# Создаем экземпляр Celery
celery_app = Celery(
    "postopus",
    broker=broker_url,
    backend=result_backend,
    include=["tasks.simple_tasks"]  # Убираем префикс src для совместимости с Render
)

# Настройки Celery (упрощенные)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 минут
    task_soft_time_limit=240,  # 4 минуты
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    # Отключаем периодические задачи для упрощения
    # beat_schedule={},
)

# Настройки для production
if os.environ.get('ENVIRONMENT') == 'production':
    celery_app.conf.update(
        worker_log_level='INFO',
        worker_hijack_root_logger=False,
        task_acks_late=True,
        worker_prefetch_multiplier=1,
    )

if __name__ == "__main__":
    celery_app.start()
