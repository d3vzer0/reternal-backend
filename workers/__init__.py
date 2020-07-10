from celery import Celery
from database import models
from celery.schedules import crontab
from environment import config, routes
import os
import logging

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
app = Celery('api', backend=config['CELERY_BACKEND'], broker=config['CELERY_BROKER'])
app.conf.task_routes = routes

app.conf.beat_schedule = {
    "trigger-email-notifications": {
        "task": "api.scheduler.task.plan",
        "schedule": 10.0
    }
}
app.conf.timezone = 'UTC'

app.autodiscover_tasks([
    'workers.search',
    'workers.scheduler'
])