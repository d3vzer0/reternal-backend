from celery import Celery
from database import models
from environment import config
import os
import logging

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
app = Celery('api', backend=config['CELERY_BACKEND'], broker=config['CELERY_BACKEND'])
app.conf.task_routes = {
    'c2.*': { 'queue': 'c2' },
    'api.*': { 'queue': 'api' },
    'search.*': { 'queue': 'search' }
}
app.autodiscover_tasks([
    'workers.search'
])