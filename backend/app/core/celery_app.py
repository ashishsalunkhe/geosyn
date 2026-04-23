from celery import Celery

from app.core.config import settings


celery_app = Celery(
    "geosyn",
    broker=settings.get_celery_broker_url(),
    backend=settings.get_celery_result_backend(),
)

celery_app.conf.update(
    task_always_eager=settings.CELERY_TASK_ALWAYS_EAGER,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "sync-signals-high-frequency": {
            "task": "app.workers.tasks.run_high_frequency_sync",
            "schedule": 900.0,
        },
        "sync-signals-anchor-cycle": {
            "task": "app.workers.tasks.run_anchor_sync",
            "schedule": 1800.0,
        },
    },
)

celery_app.autodiscover_tasks(["app.workers"])
