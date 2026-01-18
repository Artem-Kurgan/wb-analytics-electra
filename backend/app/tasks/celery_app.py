from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery = Celery(
    "electra_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Celery Beat расписание
celery.conf.beat_schedule = {
    'sync-sales-every-30-min': {
        'task': 'app.tasks.sync_tasks.sync_all_sales',
        'schedule': 1800.0,  # 30 минут
    },
    'sync-stocks-every-hour': {
        'task': 'app.tasks.sync_tasks.sync_all_stocks',
        'schedule': 3600.0,  # 1 час
    },
    'sync-products-every-6-hours': {
        'task': 'app.tasks.sync_tasks.sync_all_products',
        'schedule': 21600.0,  # 6 часов
    },
}
import os
from celery import Celery

redis_url = os.environ.get("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery("wb_analytics_electra", broker=redis_url, backend=redis_url)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
