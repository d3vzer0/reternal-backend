from app import app, celery
from app.sockets.so_connect import rsession
from app.processors import Pulse, Response
from flask_socketio import SocketIO
from app.tasks import FlaskCelery


@celery.task(name='api.result')
def emit_result(response):
    task_key = 'task-%s' %(response['task_id'])
    task_identity = rsession.get(task_key).decode('utf-8')
    session_key = 'session-%s' %(task_identity)
    identity_socket = rsession.get(session_key)
    if identity_socket:
        flask_socketio = SocketIO(message_queue=app.config['CELERY_BACKEND'])
        flask_socketio.emit('emit_result', {'data':response}, room=identity_socket.decode('utf-8'))


@celery.task(name='api.buildstate')
def emit_buildstate(platform, arch, base_url):
    build_details = {'platform':platform, 'arch':arch, 'base_url':base_url}
    flask_socketio = SocketIO(message_queue=app.config['CELERY_BACKEND'])
    flask_socketio.emit('emit_buildstate', {'data':build_details})


@celery.task(name='api.gettasks')
def pulse_agent(beacon_id, args, remote_ip, channel='http'):
    result = Pulse(beacon_id).process(args, remote_ip, 'http')
    return result


@celery.task(name='api.taskresult')
def task_result(beacon_id, task_id, args):
    result = Response(beacon_id, task_id).process(args)
    return result