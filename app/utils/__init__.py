from app.environment import config, routes
from celery import Celery
import redis

# Initialize celery for background router tasks
celery = Celery('reternal', broker=config['CELERY_BROKER'], backend=config['CELERY_BACKEND'])
celery.conf.broker_transport_options = {'fanout_patterns': True}
celery.conf.task_routes = routes

# Create redis opject for state caching 
# TODO replace with aioredis
rediscache = redis.Redis.from_url(config['REDIS_PATH_CACHE'])
