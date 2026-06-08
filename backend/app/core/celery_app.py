from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "argos",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    beat_schedule={},
)
