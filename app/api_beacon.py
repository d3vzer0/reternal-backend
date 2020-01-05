import datetime, hashlib, random,json, urllib, time
from app import app, api, jwt
from app.models import Commands, Macros, Beacons, BeaconHistory
from app.operations import Task
from app.runner import celery
from flask import Flask, request, g
from flask_restful import Api, Resource, reqparse
from mongoengine.queryset.visitor import Q
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)

from bson.json_util import dumps as loadbson


class APIAgents(Resource):
    decorators = []

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('operating_system', type=str, required=False, location='args', default='')
        self.parser.add_argument('name', type=str, required=False, location='args', default='')
        self.parser.add_argument('integration', type=str, required=True, location='args')

    def get(self):
        args = self.parser.parse_args()
        get_tasks = celery.send_task('c2.system.agents', args=(args.integration,)).get()
        if not get_tasks['get']: return {'agents': { } }
        get_agents = celery.send_task(get_tasks['get']).get()
        return get_agents

api.add_resource(APIAgents, '/api/v1/agents')


class APICredentials(Resource):
    decorators = [jwt_required]

    def get(self):
        credentials = Credentials.objects()
        result = json_loads(credentials.to_json())
        return result

api.add_resource(APICredentials, '/api/v1/credentials')


class APIBeacon(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('beacon_id', type=str, required=True, location='args')
        self.parser.add_argument('limit', type=int, required=True, location='args')
        self.parser.add_argument('skip', type=int, required=True, location='args')
        self.parser.add_argument('start_date', type=int, required=False, location='args', default=1514764800)
        self.parser.add_argument('end_date', type=int, required=False, location='args',
            default=int(datetime.datetime.now().timestamp()))

    def get(self):
        args = self.parser.parse_args()
        if args['limit'] > 1000:
            args['limit'] = 1000

        start_date = datetime.datetime.fromtimestamp(args.start_date )
        end_date = datetime.datetime.fromtimestamp(args.end_date)
        beacon_history = BeaconHistory.objects(beacon_id=args.beacon_id, timestamp__lte=end_date,
            timestamp__gte=start_date).skip(args['skip']).limit(args['limit'])

        history_count = BeaconHistory.objects.count()
        json_object = json.loads(beacon_history.to_json())
        result = {"data":json_object, "count":history_count}
        return result

api.add_resource(APIBeacon, '/api/v1/history')


class APIBeaconTasks(Resource):
    decorators = [jwt_required]

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

api.add_resource(APIBeaconTasks, '/api/v1/agent/tasks/<string:beacon_id>')


