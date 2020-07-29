from app.workers import celery
from app.environment import config
import socketio
import redis

# TODO replace with aioredis
rediscache = redis.Redis.from_url(config['REDIS_PATH_CACHE'])
esio = socketio.RedisManager(config['REDIS_PATH_SOCKETIO'], write_only=True)

# emit an event
@celery.task(name='api.websocket.result.transmit')
def transmit_result(task_response, task_id, user=None):
    user_session = rediscache.get(user).decode('utf-8')
    esio.emit('result', {'task': task_id}, room=user_session)
