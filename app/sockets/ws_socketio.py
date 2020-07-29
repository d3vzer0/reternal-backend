# from app import celery
from app.utils.jwt_validation import JWT
from app.utils import rediscache
from app.environment import config
from app.main import app, sio, sio_asgi_app
from jwt.exceptions import (InvalidTokenError, InvalidSignatureError, ExpiredSignatureError,
    InvalidAudienceError, InvalidIssuerError, InvalidIssuedAtError, ImmatureSignatureError, InvalidAlgorithmError)
from socketio.exceptions import ConnectionRefusedError
from datetime import timedelta


def validate_session(environ):
    # Todo, validate session sources etc
    if 'HTTP_AUTHORIZATION' in environ:
        access_token = environ['HTTP_AUTHORIZATION'].replace('Bearer ', '')
        try:
            validate_token = JWT(config['OAUTH2_OPENID_CONFIG'], config['OAUTH2_ISSUER'],
                config['OAUTH2_AUDIENCE']).validate(access_token)
            return validate_token

        except InvalidTokenError:
            raise ConnectionRefusedError('Invalid access_token supplied')

        except InvalidAlgorithmError:
            raise ConnectionRefusedError('Invalid algorithm for access_token')
        
        except InvalidSignatureError:
            raise ConnectionRefusedError('Could not validate access_token signature')

        except ExpiredSignatureError:
            raise ConnectionRefusedError('Expired access_token')

        except InvalidIssuedAtError:
            raise ConnectionRefusedError('Invalid issued date for access_token')

        except InvalidIssuerError:
            raise ConnectionRefusedError('Invalid issuer for access_token')

        except ImmatureSignatureError:
            raise ConnectionRefusedError('Signature validation error for access_token')

        except InvalidAudienceError:
            raise ConnectionRefusedError('Unauthorized audience for access_token')

        except Exception as err:
            raise ConnectionRefusedError('Unauthorized')

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
    # TODO Replace with async
    rediscache.setex(authorize_user['email'], timedelta(minutes=60),
        value=sid
    )
    await sio.save_session(sid, { 'email': authorize_user['email'],
        'family_name': authorize_user['family_name'],
        'given_name': authorize_user['given_name'], 
        'ipaddr': authorize_user['ipaddr'], 'name': authorize_user['name']
    })

@sio.on('disconnect')
async def socketio_disconnect(sid):
    user_session = await sio.get_session(sid)
    rediscache.delete(user_session['email'])

app.mount('/', sio_asgi_app)
