from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from .environment import config
from .routers.v1.main import api_v1

# Initialise FastAPI + CORS 
app = FastAPI()

# Init CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:9090'],
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'DELETE', 'OPTIONS'],
    allow_headers=["*"],
)

# Include v1 endpoints
app.include_router(api_v1, prefix=config['API_PATH'])

# Import database, socket and custom exception handler
from . import exceptions
from .sockets.ws_connect import socketio_connect
from .sockets.ws_disconnect import socketio_disconnect
from .sockets.ws_notifications import on_notification

