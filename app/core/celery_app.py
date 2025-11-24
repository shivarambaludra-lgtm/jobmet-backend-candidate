from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "jobmet",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.search_tasks",
        "app.tasks.email_tasks",
        "app.tasks.cleanup_tasks"
    ]
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    broker_connection_retry_on_startup=True,
)

# Periodic tasks (cron-like scheduling)
celery_app.conf.beat_schedule = {
    "cleanup-old-searches": {
        "task": "app.tasks.cleanup_tasks.cleanup_old_searches",
        "schedule": 3600.0,  # Every hour
    },
    "cleanup-old-activities": {
        "task": "app.tasks.cleanup_tasks.cleanup_old_activities",
        "schedule": 86400.0,  # Daily
    },
    "cleanup-inactive-jobs": {
        "task": "app.tasks.cleanup_tasks.cleanup_inactive_jobs",
        "schedule": 86400.0,  # Daily
    },
    "send-saved-search-alerts": {
        "task": "app.tasks.email_tasks.send_saved_search_alerts",
        "schedule": crontab(hour=9, minute=0),  # Daily at 9 AM
    },
}
