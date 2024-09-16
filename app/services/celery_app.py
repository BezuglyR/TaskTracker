import os

from celery import Celery

from app.config import settings

celery = Celery(
    "tasks",
    include=["app.services.tasks"],
)
celery.conf.broker_url = os.environ.get(
    "CELERY_BROKER_URL",
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
)
celery.conf.result_backend = os.environ.get(
    "CELERY_RESULT_BACKEND",
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
)
