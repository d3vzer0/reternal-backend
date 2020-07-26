from fastapi import FastAPI
from .environment import config
from starlette.middleware.cors import CORSMiddleware
from .routers import (api_agents, api_campaigns, api_coverage,
    api_graph, api_listeners, api_mapping, api_mitre, api_modules,
    api_results, api_scheduler, api_search, api_sigma, api_stagers,
    api_states, api_stats, api_tasks, api_workers)
import socketio


# Initialise FastAPI + CORS 
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:9090'],
    allow_credentials=True,
    # allow_methods=['GET', 'POST', 'DELETE', 'OPTIONS'],
    allow_headers=["*"],
)

# Initialise socket.io
rmgr = socketio.AsyncRedisManager(config['REDIS_PATH_SOCKETIO'])
sio = socketio.AsyncServer(client_manager=rmgr, cors_allowed_origins=[])
sio_asgi_app = socketio.ASGIApp(sio)

# Import API endpoints
app.include_router(api_agents.router, prefix=config['API_PATH'], tags=['agents'])
app.include_router(api_campaigns.router, prefix=config['API_PATH'], tags=['campaigns'])
app.include_router(api_coverage.router, prefix=config['API_PATH'], tags=['coverage'])
app.include_router(api_graph.router, prefix=config['API_PATH'], tags=['graph'])
app.include_router(api_listeners.router, prefix=config['API_PATH'], tags=['listeners'])
app.include_router(api_mapping.router, prefix=config['API_PATH'], tags=['mapping'])
app.include_router(api_mitre.router, prefix=config['API_PATH'], tags=['mitre'])
app.include_router(api_modules.router, prefix=config['API_PATH'], tags=['modules'])
app.include_router(api_results.router, prefix=config['API_PATH'], tags=['results'])
app.include_router(api_scheduler.router, prefix=config['API_PATH'], tags=['scheduler'])
app.include_router(api_search.router, prefix=config['API_PATH'], tags=['search'])
app.include_router(api_sigma.router, prefix=config['API_PATH'], tags=['sigma'])
app.include_router(api_stagers.router, prefix=config['API_PATH'], tags=['stagers'])
app.include_router(api_states.router, prefix=config['API_PATH'], tags=['states'])
app.include_router(api_stats.router, prefix=config['API_PATH'], tags=['stats'])
app.include_router(api_tasks.router, prefix=config['API_PATH'], tags=['tasks'])
app.include_router(api_workers.router, prefix=config['API_PATH'], tags=['workers'])

# Import database, socket and custom exception handler
from app import exceptions
from app.database.models import *
from app.sockets.ws_socketio import *

