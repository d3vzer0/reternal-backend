from fastapi import FastAPI
from celery import Celery
from app.environment import config
from starlette.middleware.cors import CORSMiddleware


api = FastAPI()
api.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:9090'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

celery = Celery('reternal', broker=config['CELERY_BROKER'],
    backend=config['CELERY_BACKEND'])

celery.conf.broker_transport_options = {'fanout_prefix': True}
celery.conf.broker_transport_options = {'fanout_patterns': True}
celery.conf.task_routes = {
    'c2.*': { 'queue': 'c2' },
    'api.*': { 'queue': 'api' }    
}

from app.database.models import *
from app.database.exceptions import *
from app.api_workers import *
from app.api_listeners import *
from app.api_agents import *
from app.api_modules import *
from app.api_mitre import *
from app.api_mapping import *
from app.api_stagers import *
from app.api_tasks import *
from app.api_graph import *
from app.api_campaigns import *
from app.api_scheduler import *
from app.api_results import *