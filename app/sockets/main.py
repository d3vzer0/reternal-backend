from app.environment import config
from app.main import app
import socketio

rmgr = socketio.AsyncRedisManager(config['REDIS_PATH_SOCKETIO'])
sio = socketio.AsyncServer(client_manager=rmgr, cors_allowed_origins=[])
sio_asgi_app = socketio.ASGIApp(sio)
app.mount('/', sio_asgi_app)
