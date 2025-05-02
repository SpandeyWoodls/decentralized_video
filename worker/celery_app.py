# decentralized_video/worker/celery_app.py

import os
from celery import Celery

# Configure broker and result backend via environment variables
BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

# Initialize Celery app
celery_app = Celery(
    "decentralized_video",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
)

# Automatically discover tasks in the worker.tasks module
celery_app.autodiscover_tasks(["decentralized_video.worker.tasks"])
