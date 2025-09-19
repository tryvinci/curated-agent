from celery import Celery
from app.core.config import get_settings

settings = get_settings()

# Create Celery instance
celery_app = Celery(
    "curated-agent",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.creative_workflow"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,  # 1 hour
)