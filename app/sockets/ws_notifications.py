from app.utils import rediscache
from .main import sio


@sio.on('notification')
async def on_notification(sid, data):
    user_session = await sio.get_session(sid) 
    message_content = {'from': user_session['name'], 'content': data}
    await sio.emit('notification', message_content, room='notifications')
