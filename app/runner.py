from app import app
from app.sockets.so_connect import rsession
from flask_socketio import SocketIO
from app.tasks import FlaskCelery

celery = FlaskCelery(app).make()


@celery.task(name='api.result')
def emit_result(response):
    task_key = 'task-%s' %(response['task_id'])
    task_identity = rsession.get(task_key).decode('utf-8')
    session_key = 'session-%s' %(task_identity)
    identity_socket = rsession.get(session_key).decode('utf-8')
    flask_socketio = SocketIO(message_queue=app.config['CELERY_BACKEND'])
    flask_socketio.emit('emit_result', {'data':response}, room=identity_socket)