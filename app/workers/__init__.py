from celery import Celery
from app.environment import config, routes
import os
import logging

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
celery = Celery('api', backend=config['CELERY_BACKEND'], broker=config['CELERY_BROKER'])
celery.conf.task_routes = routes

celery.conf.beat_schedule = {
    "trigger-email-notifications": {
        "task": "api.scheduler.task.plan",
        "schedule": 10.0
    }
}
celery.conf.timezone = 'UTC'

celery.autodiscover_tasks([
    # 'app.workers.search',
    # 'app.workers.scheduler',
    'app.workers.websocket'
])