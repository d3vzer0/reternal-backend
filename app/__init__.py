from celery import Celery
from flask import Flask
from flask_restful import Api, Resource
from flask_mongoengine import MongoEngine
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.tasks.task_celery import FlaskCelery

#Initialize Flask Instance
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app)
jwt = JWTManager(app)

# Initialize DB and load models and views
from  app.configs import *
db = MongoEngine(app)
celery = FlaskCelery.make(app)

# Import views
from app import api_generic
from app import api_mitre
from app import api_commands
from app import api_pulse
from app import api_beacon
from app import api_results
from app import api_tasks
from app import api_payload
from app import api_macros
from app import api_startuptasks