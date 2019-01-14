import datetime, hashlib, random,json, urllib, time
from app import app, api, celery, jwt
from app.models import Commands, Tasks, TaskResults, BeaconHistory
from app.operations import Task, Result
from flask import Flask, request, g, make_response
from flask_restful import Api, Resource, reqparse
from mongoengine.queryset.visitor import Q
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)
from bson.json_util import dumps as loadbson

class APIResults(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.args = reqparse.RequestParser()
        if request.method == "GET":
            content_choices = ('image', 'text', 'other')
            self.args.add_argument('beacon_id', location='args', required=True, help='Beacon ID', type=str)
            self.args.add_argument('content_type', location='args', required=True, help='Content Type (Magic)', choices=content_choices, type=str)

    def get(self):
        args = self.args.parse_args()
        content_mapping = {
            'image':'image/png',
            'text':'text/plain',
            'other':''
        }
        pipeline = [{'$lookup': {"from":"fs.files", "as":"file", "let":{"file_id":"$output"},
            "pipeline":[{"$match":{"$expr":{"$and":[{"$eq":["$_id", "$$file_id"]}, {"$eq":["$contentType", content_mapping[args.content_type]]}]}}}]}},{'$unwind':'$file'}]
        task_results = TaskResults.objects(beacon_id=args.beacon_id).aggregate(*pipeline)
        results = json.loads(loadbson(task_results))
        return {'count':0, 'data':results}



api.add_resource(APIResults, '/api/v1/results')


class APIAttachment(Resource):
    decorators = [jwt_required]

    def get(self, task_id):
        task_result = TaskResults.objects.get(id=task_id)
        task_file = task_result.output.read()
        response = make_response(task_file)
        response.headers['Content-Type'] = task_result.output.contentType
        return response

    def delete(self, task_id):
        deleteTask = Task.delete(task_id)
        return deleteTask

api.add_resource(APIAttachment, '/api/v1/result/<string:task_id>')

