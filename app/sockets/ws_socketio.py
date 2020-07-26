# from app import celery
from app.utils.jwt_validation import JWT
from app.environment import config
from app.main import app, sio, sio_asgi_app
from socketio.exceptions import ConnectionRefusedError


def validate_session(environ):
    # Todo, validate session sources etc
    if 'HTTP_AUTHORIZATION' in environ:
        access_token = environ['HTTP_AUTHORIZATION'].replace('Bearer ', '')
        validate_token = JWT(config['OAUTH2_OPENID_CONFIG'], config['OAUTH2_ISSUER'],
            config['OAUTH2_AUDIENCE']).validate(access_token)
        return validate_token
    else:
        raise ConnectionRefusedError('Authentication required')

@sio.on('notification')
async def on_notification(sid, data):
    user_session = await sio.get_session(sid) 
    message_content = {'from': user_session['name'], 'content': data}
    await sio.emit('notification', message_content, room='notifications')

@sio.on('connect')
async def socketio_connect(sid, environ):
    authorize_user = validate_session(environ)
    sio.enter_room(sid, 'notifications')
    sio.enter_room(sid, 'tasks')
    await sio.save_session(sid, { 'email': authorize_user['email'],
        'family_name': authorize_user['family_name'],
        'given_name': authorize_user['given_name'], 
        'ipaddr': authorize_user['ipaddr'], 'name': authorize_user['name']
    })

app.mount('/', sio_asgi_app)
