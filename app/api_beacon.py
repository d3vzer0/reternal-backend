import datetime, hashlib, random,json, urllib, time
from app import app, api, celery, jwt
from app.models import Commands, Macros, Beacons, BeaconHistory
from app.operations import Task
from flask import Flask, request, g
from flask_restful import Api, Resource, reqparse
from mongoengine.queryset.visitor import Q
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)


class APIBeacons(Resource):
    decorators = []

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('platform', type=str, required=False, location='args', default="")
        self.parser.add_argument('search', type=str, required=False, location='args', default="")

    def get(self):
        args = self.parser.parse_args()
        get_beacons = Beacons.objects(Q(platform__contains=args['platform']) & (Q(username__contains=args['search']) | Q(hostname__contains=args['search'])))
        beacon_list=[]
        for beacon in get_beacons:
            last_pulse = BeaconHistory.objects(beacon_id=str(beacon.beacon_id)).first()
            last_timestamp = last_pulse.timestamp
            beacon_timer = int(beacon.timer) * 1.80
            compare_date = last_timestamp + datetime.timedelta(seconds=int(beacon_timer))
            current_date = datetime.datetime.now()
            online_state = "offline" if current_date > compare_date else "online"
            beacon_data = {"beacon_id":beacon.beacon_id, "state":online_state, "timer":beacon.timer,
                "username":beacon.username, "platform":beacon.platform, "remote_ip":beacon.remote_ip,
                "last_beacon":str(last_timestamp), "hostname":beacon.hostname}
            beacon_list.append(beacon_data)

        return beacon_list

api.add_resource(APIBeacons, '/api/v1/agents')


class APICredentials(Resource):
    decorators = []

    def get(self):
        credentials = Credentials.objects()
        result = json_loads(credentials.to_json())
        return result

api.add_resource(APICredentials, '/api/v1/credentials')


class APIBeacon(Resource):
    decorators = []

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('limit', type=int, required=True, location='args')
        self.parser.add_argument('skip', type=int, required=True, location='args')

    def get(self, beacon_id):
        args = self.parser.parse_args()
        if args['limit'] > 1000:
            args['limit'] = 1000

        beacon_history = BeaconHistory.objects(beacon_id=beacon_id).skip(args['skip']).limit(args['limit'])
        history_count = BeaconHistory.objects.count()
        json_object = json.loads(beacon_history.to_json())
        result = {"data":json_object, "count":history_count}
        return result

api.add_resource(APIBeacon, '/api/v1/agent/<string:beacon_id>')



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