import datetime, hashlib, random,json, urllib, time
from app import app, api, celery, jwt
from app.models import Commands, Tasks, TaskResults, BeaconHistory
from app.operations import Task, Result
from app.validators import Existance
from flask import Flask, request, g
from flask_restful import Api, Resource, reqparse
from mongoengine.queryset.visitor import Q
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)
from bson.json_util import dumps as loadbson

class APIResults(Resource):
    decorators = []

    def __init__(self):
        self.args = reqparse.RequestParser()
        if request.method == "POST":
            self.args.add_argument('beacon_id', location='json', required=True, help='Beacon ID', type=str)
            self.args.add_argument('task_id', location='json', required=True, help='Task ID', type=str)
        if request.method == "GET":
            self.args.add_argument('beacon_id', location='args', required=True, help='Beacon ID', type=str)

    def get(self):
        args = self.args.parse_args()
        pipeline = [{"$lookup": {"from": "task_results", "localField": "_id","foreignField": "task_id", "as": "output"}}]
        task_results = Tasks.objects(beacon_id=args.beacon_id).aggregate(*pipeline)
        results = json.loads(loadbson(task_results))
        # for output in task_results:
        #     result = {"beacon_id":output.beacon_id, "task_id":output.task_id, "end_date":output.end_date}
        #     results.append(result)
        return results



api.add_resource(APIResults, '/api/v1/results')


class APIAttachment(Resource):
    decorators = []

    def get(self, task_id):
        task_result = TaskResults.objects.get(taskId=task_id)
        task_file = task_result.output.read()
        filename = "%s-output" %(task_id)
        response = make_response(task_file)
        response.headers['Content-Type'] = "application/octet-stream"
        response.headers["Content-Disposition"] = "attachment; filename=%s" %(filename)
        return response

    def delete(self, task_id):
        deleteTask = Task.delete(task_id)
        return deleteTask

api.add_resource(APIAttachment, '/api/v1/result/<string:task_id>')
