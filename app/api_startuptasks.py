from app import app, api, jwt
from app.models import StartupTasks
from app.operations import StartupTask
from flask import Flask, request, g
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)
from bson.json_util import dumps
import json
import datetime


class APIStartupTask(Resource):
    decorators = [jwt_required]

    def delete(self, startup_id):
        result = StartupTask.delete(startup_id)
        return result

api.add_resource(APIStartupTask, '/api/v1/startuptask/<string:startup_id>')


class APIStartupTasks(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.args = reqparse.RequestParser()
        if request.method == 'POST':
            self.args.add_argument('commands', type=list, required=True, location='json')
            self.args.add_argument('platform', type=str, required=True, location='json', choices=("Windows", "Linux", "macOS"))
            self.args.add_argument('name', type=str, required=True, location='json')

        if request.method == 'GET':
            self.args.add_argument('platform', type=str, required=True, location='args', choices=("Windows", "Linux", "macOS"))


    def get(self):
        args = self.args.parse_args()
        startup_tasks = StartupTasks.objects(platform=args.platform)
        result = json.loads(startup_tasks.to_json())
        return result

    def post(self):
        args = self.args.parse_args()
        result = StartupTask.create(args.platform, args.commands, args.name)
        return result


api.add_resource(APIStartupTasks, '/api/v1/startuptasks')
