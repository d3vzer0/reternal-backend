from app.utils import rediscache
from .main import sio


@sio.on('disconnect')
async def socketio_disconnect(sid):
    user_session = await sio.get_session(sid)
    rediscache.delete(user_session['email'])

