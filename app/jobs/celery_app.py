from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "water_break_watch",
    broker=settings.redis_url,
    backend=settings.redis_url,
)
celery_app.conf.task_default_queue = "ingest"
celery_app.autodiscover_tasks(["app.jobs"])
