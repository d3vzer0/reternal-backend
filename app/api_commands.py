from app import app, api, celery, jwt
from app.models import Commands
from app.validators import Existance
from flask import Flask, request, g
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)
from bson.json_util import dumps
import json


class APICommands(Resource):
    decorators = [jwt_required]

    def get(self):
        get_commands = Commands.objects()
        json_object = json.loads(get_commands.to_json())
        return json_object
        

api.add_resource(APICommands, '/api/v1/commands')

