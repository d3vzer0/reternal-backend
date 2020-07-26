# from app import celery
from app.main import app, sio, sio_asgi_app

@sio.on('rawr')
async def hello_there(sid, data):
    await sio.emit('kenobi', {'':''}, room=sid)

@sio.on('connect')
async def socketio_connect(sid, environ):
    # do auth here
    print(environ)

@sio.on('disconnect')
async def socketio_disconnect(sid):
    print(sid)

app.mount('/', sio_asgi_app)

