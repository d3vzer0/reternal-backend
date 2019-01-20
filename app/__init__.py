from celery import Celery
from flask import Flask
from flask_restful import Api, Resource
from flask_mongoengine import MongoEngine
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO
from app.tasks.task_celery import FlaskCelery

#Initialize Flask Instance
app = Flask(__name__)
api = Api(app)
jwt = JWTManager(app)

# Initialize DB and load models and views
from  app.configs import *
celery = FlaskCelery(app).make()
socketio = SocketIO(app, message_queue=app.config['CELERY_BACKEND'])
db = MongoEngine(app)
CORS(app, resources={r"/api/*": {"origins": app.config['CORS_DOMAIN']}})


# Import views
from app import api_generic
from app import api_mitre
from app import api_commands
from app import api_beacon
from app import api_results
from app import api_tasks
from app import api_payload
from app import api_macros
from app import api_startuptasks
from app import api_stats
from app import api_mapping
from app import api_recipes
from app.sockets import so_connect