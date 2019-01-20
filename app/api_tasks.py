import datetime, hashlib, random,json, urllib, time
from bson.json_util import dumps as loadbson
from app.sockets import rsession
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
            self.args.add_argument('name', type=str, required=True, location='json')
            self.args.add_argument('commands', type=list, required=True, location='json')
            self.args.add_argument('beacon_id', type=str, required=True, location='json')
            self.args.add_argument('start_date', type=int, required=False,
                default=int(datetime.datetime.now().timestamp()), location='json')

        if request.method == "GET":
            self.args.add_argument('beacon_id', location='args', required=True, help='Beacon ID', type=str)
            self.args.add_argument('start_date', type=int, required=False, location='args', default=1514764800)
            self.args.add_argument('name', type=str, required=False, default='')
            self.args.add_argument('end_date', type=int, required=False, location='args',
                default=int(datetime.datetime.now().timestamp()))

    def get(self):
        args = self.args.parse_args()
        pipeline = [{"$lookup": {"from": "task_results", "localField": "_id","foreignField": "task_id", "as": "output"}}]
        start_date = datetime.datetime.fromtimestamp(args.start_date )
        end_date = datetime.datetime.fromtimestamp(args.end_date)
        task_results = Tasks.objects(beacon_id=args.beacon_id, start_date__gte=start_date,
            start_date__lte=end_date, name__contains=args.name).aggregate(*pipeline)
        results = json.loads(loadbson(task_results))
        return {'count':len(results), 'data':results}

    def post(self):
        args = self.args.parse_args()
        verify_beacon = Beacon(args.beacon_id).get()
        if verify_beacon['result'] == "success":
            start_date = datetime.datetime.fromtimestamp(args.start_date)
            result = Task().create(args.beacon_id, args.commands, start_date, args.name)
            task_key = 'task-%s' %(result['data']['task_id'])
            rsession.set(task_key, get_jwt_identity(), ex=3600)
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
