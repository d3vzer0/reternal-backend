from celery import Celery
from flask import Flask
from flask_restful import Api, Resource
from app.functions_generic import make_celery
from flask_mongoengine import MongoEngine
from flask_jwt_extended import JWTManager
from flask_cors import CORS

#Initialize Flask Instance
app = Flask(__name__)
api = Api(app)
cors = CORS(app)
jwt = JWTManager(app)

# Initialize DB and load models and views
from app.configs import variables
db = MongoEngine(app)
celery = make_celery(app)

# Import views
from app import api_generic