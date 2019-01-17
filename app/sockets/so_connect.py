from app import app, socketio
from flask import request
from flask_socketio import SocketIO, disconnect
import redis
import threading
import jwt
import os

rsession = redis.Redis(host=app.config['REDIS_IP'], port=app.config['REDIS_PORT'], db=app.config['REDIS_DB'])

def jwt_validate(token):
    try:
        decoded = jwt.decode(token, app.config['JWT_SECRET_KEY'])
        result = {'result':'success', 'data':decoded}

    except jwt.exceptions.ExpiredSignature:
        result = {'result':'expired', 'data':'Token expired'}

    except jwt.exceptions.InvalidTokenError:
        result = {'result':'invalid', 'data':'Invalid token'}

    except Exception:
        result = {'result':'failed', 'data':'Unable to decode token'}

    return result


def verify_session(identity):
    socket_key = 'socket-%s' %(identity)
    session_state = rsession.get(socket_key).decode('utf-8')
    if not session_state or session_state == 'Unauthenticated':
        disconnect(identity)


@socketio.on('connect')
def connectsocket():
    sid = request.sid
    threading.Timer(2.0, verify_session, args=(sid,))


@socketio.on('authenticate')
def authenticate(token):
    sid = request.sid
    decode_token = jwt_validate(token['access_token'])
    if decode_token['result'] == 'success':
        socket_key = 'socket-%s' %(sid)
        session_key = 'session-%s' %(decode_token['data']['identity'])
        rsession.set(socket_key, 'Authenticated', ex=2500)
        rsession.set(session_key, sid, ex=2500)
    else:
        disconnect()