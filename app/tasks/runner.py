from app import celery, app
from app.sockets.so_connect import rsession
from flask_socketio import SocketIO


@celery.task(name='api.result')
def emit_result(response):
    session_key = 'session-%s' %(response['identity'])
    user_session = rsession.get(session_key).decode('utf-8')
    flask_socketio = SocketIO(message_queue=app.config['CELERY_BACKEND'])
    flask_socketio.emit('emit_result', {'data':response['result']}, room=user_session)