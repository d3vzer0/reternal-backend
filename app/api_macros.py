from app import app, api, celery, jwt
from app.models import Macros
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
    decorators = [jwt_required]

    def delete(self, macro_id):
        result = Macro.delete(macro_id)
        return result

api.add_resource(APIMacro, '/api/v1/macro/<string:macro_id>')


class APIMacros(Resource):
    decorators = [jwt_required]

    def __init__(self):
        if request.method == 'POST':
            self.parser = reqparse.RequestParser()
            self.parser.add_argument('name', type=str, required=True, location='json')
            self.parser.add_argument('command', type=str, required=True, location='json')
            self.parser.add_argument('input', type=str, required=True, location='json')


    def get(self):
        macro_list = Macros.objects()
        result = json.loads(macro_list.to_json())
        return result


    def post(self):
        args = self.parser.parse_args()
        verify_command = Existance.command(args.command)
        if verify_command['result'] == "exists":
            result = Macro.create(args.name, args.command, args.input)
        else:
            result = verify_command

        return result

api.add_resource(APIMacros, '/api/v1/macros')
