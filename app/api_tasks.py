import datetime, hashlib, random,json, urllib, time
from app import app, api, celery, jwt
from app.models import Tasks
from app.operations import Task
from app.validators import Existance
from flask import Flask, request, g
from flask_restful import Api, Resource, reqparse
from mongoengine.queryset.visitor import Q
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)

class APITasks(Resource):
    decorators = []

    def __init__(self):
        self.parser = reqparse.RequestParser()
        if request.method == 'POST':
            self.parser.add_argument('commands', type=list, required=True, location='json')
            self.parser.add_argument('beacon_id', type=str, required=True, location='json')
            self.parser.add_argument('type', type=str, required=True, location='json')
            self.parser.add_argument('task', type=str, required=True, location='json')

    def post(self):
        args = self.parser.parse_args()
        verify_beacon = Existance.beacon(beacon_id=args['beacon_id'])
        if verify_beacon['result'] == "success":
            result = Task.create(args['beacon_id'], args['type'], args['task'], args['commands'])
        else:
            result = verify_beacon

        return result

 
api.add_resource(APITasks, '/api/v1/tasks')


class APITask(Resource):
    decorators = []

    def get(self, task_id):
        task_details = Task.get(task_id)
        return task_details

    def delete(self, task_id):
        result = Task.delete(task_id)
        return result


api.add_resource(APITask, '/api/v1/task/<string:task_id>')
