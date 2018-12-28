from app import app, api, celery, jwt
from app.models import Commands, Macros
from app.operations import Macro
from app.validators import Existance
from flask import Flask, request, g
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)
from bson.json_util import dumps
import json


class APIMacro(Resource):
    decorators = []

    def delete(self, macro_id):
        username = get_jwt_identity()
        delete_macro = Macro.delete(username, alias_id)
        return jsonify(delete_macro)

api.add_resource(APIMacro, '/api/v1/macro/<string:macro_id>')


class APIMacros(Resource):
    decorators = []

    def __init__(self):
        if request.method == 'POST':
            self.parser = reqparse.RequestParser()
            self.parser.add_argument('macro_name', type=str, required=True, location='json')
            self.parser.add_argument('command_name', type=str, required=True, location='json')
            self.parser.add_argument('input', type=str, required=True, location='json')


    def post(self):
        args = self.parser.parse_args()
        verify_command = Existance.command(args['commandIdentifier'])
        if verify_command['result'] == "exists":
            username = get_jwt_identity()
            result = Macro.create(username, verify_command['data'], args['macro_name'], args['input'])
        else:
            result = verify_command

        return result

api.add_resource(APIMacros, '/api/v1/macros')


class APICommands(Resource):
    decorators = []

    def get(self):
        get_commands = Commands.objects()
        json_object = json.loads(get_commands.to_json())
        return json_object
        

api.add_resource(APICommands, '/api/v1/commands')

