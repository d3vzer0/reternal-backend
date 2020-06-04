from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from celery import Celery
from environment import config, routes
from starlette.middleware.cors import CORSMiddleware


api = FastAPI()

api.add_middleware(
    CORSMiddleware,
    allow_origins=[config['CORS_ALLOW_ORIGIN']],
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'DELETE', 'OPTIONS'],
    allow_headers=["*"],
)

celery = Celery('reternal', broker=config['CELERY_BROKER'], backend=config['CELERY_BACKEND'])
celery.conf.broker_transport_options = {'fanout_prefix': True}
celery.conf.broker_transport_options = {'fanout_patterns': True}
celery.conf.task_routes = routes

from database.models import *
from app.exceptions import *
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
from app.api_validations import *
from app.api_search import *
from app.api_coverage import *
# from app.api_stats import *
from app.api_states import *
