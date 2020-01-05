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
