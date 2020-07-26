from celery import Celery
from .environment import config, routes
import redis

# Create redis opject for state caching
rediscache = redis.Redis.from_url(config['REDIS_PATH_CACHE'])

# Initialize celery for background tasks
celery = Celery('reternal', broker=config['CELERY_BROKER'], backend=config['CELERY_BACKEND'])
celery.conf.broker_transport_options = {'fanout_patterns': True}
celery.conf.task_routes = routes
