from celery import Celery

from src.core.config import settings

celery_app = Celery(
    "admission_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
    include=["src.tasks.admission"],
    beat_schedule={
        "scrape-all-universities": {
            "task": "src.tasks.admission.scrape_all_universities",
            "schedule": settings.CELERY_BEAT_SCHEDULE_INTERVAL,
        },
    },
)
