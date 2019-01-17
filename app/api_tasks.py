import datetime, hashlib, random,json, urllib, time
from bson.json_util import dumps as loadbson
from app import app, api, jwt
from app.models import Tasks, TaskResults
from app.operations import Task, Beacon
from flask import Flask, request, g
from flask_restful import Api, Resource, reqparse
from mongoengine.queryset.visitor import Q
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)


class APITasks(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.args = reqparse.RequestParser()
        if request.method == 'POST':
            date_epoch = int(datetime.datetime.now().timestamp())
            self.args.add_argument('name', type=str, required=True, location='json')
            self.args.add_argument('commands', type=list, required=True, location='json')
            self.args.add_argument('beacon_id', type=str, required=True, location='json')
            self.args.add_argument('start_date', type=int, required=False, default=date_epoch, location='json')

        if request.method == "GET":
            self.args.add_argument('beacon_id', location='args', required=True, help='Beacon ID', type=str)

    def get(self):
        args = self.args.parse_args()
        pipeline = [{"$lookup": {"from": "task_results", "localField": "_id","foreignField": "task_id", "as": "output"}}]
        task_results = Tasks.objects(beacon_id=args.beacon_id).aggregate(*pipeline)
        results = json.loads(loadbson(task_results))
        return {'count':30, 'data':results}

    def post(self):
        args = self.args.parse_args()
        verify_beacon = Beacon(args.beacon_id).get()
        if verify_beacon['result'] == "success":
            start_date = datetime.datetime.fromtimestamp(args.start_date)
            result = Task().create(args.beacon_id, args.commands, start_date, args.name)
        else:
            result = verify_beacon

        return result

 
api.add_resource(APITasks, '/api/v1/tasks')


class APITask(Resource):
    decorators = [jwt_required]

    def get(self, task_id):
        task_details = Task.get(task_id)
        return task_details

    def delete(self, task_id):
        result = Task.delete(task_id)
        return result


api.add_resource(APITask, '/api/v1/task/<string:task_id>')
