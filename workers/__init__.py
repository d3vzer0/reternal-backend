from celery import Celery
from database import models
from environment import config, routes
import os
import logging

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
app = Celery('api', backend=config['CELERY_BACKEND'], broker=config['CELERY_BACKEND'])
app.conf.task_routes = routes

app.autodiscover_tasks([
    'workers.search'
])