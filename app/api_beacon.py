import datetime, hashlib, random,json, urllib, time
from app import app, api, celery, jwt
from app.models import Commands, Macros, Beacons, BeaconHistory
from operations import Task
from flask import Flask, request, g
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)


class APIBeacons(Resource):
    decorators = []

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('platform', type=str, required=False, location='args')
        self.parser.add_argument('hostname', type=str, required=False, location='args')
        self.parser.add_argument('username', type=str, required=False, location='args')

    def get(self):
        args = self.parser.parse_args()
        raw_query= {}
        for argument in args:
            if args[argument]:
                raw_query[argument] = args[argument]

        beacon_list=[]
        get_beacons = Beacons.objects(__raw__=raw_query)
        for beacon in get_beacons:
            last_pulse = BeaconHistory.objects(beacon_id=str(beacon.beacon_id)).first()
            last_timestamp = last_pulse.timestamp
            beacon_timer = int(beacon.timer) * 1.80
            compare_date = last_timestamp + datetime.timedelta(seconds=int(beacon_timer))
            current_date = datetime.datetime.now()
            online_state = "offline" if current_date > compare_date else "online"
            beacon_data = {"beacon_id":beacon.beacon_id, "state":online_state, "timer":beacon.timer,
                "username":beacon.username, "platform":beacon.platform, "remote_ip":beacon.remote_ip,
                "last_beacon":str(last_timestamp)}
            beacon_list.append(beacon_data)

        return beacon_list

api.add_resource(APIBeacons, '/api/v1/beacons')


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
        self.parser.add_argument('limit', type=int, required=False, location='args', default=200)

    def get(self, beacon_id):
        args = self.parser.parse_args()
        if args['limit'] > 1000:
            args['limit'] = 1000

        beacon_history = BeaconHistory.objects(beacon_id=beacon_id).limit(args['limit'])
        result = json.loads(beacon_history.to_json())
        return result

api.add_resource(APIBeacon, '/api/v1/beacon/<string:beacon_id>')



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