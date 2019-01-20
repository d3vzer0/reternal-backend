import datetime, hashlib, random,json, urllib, time
from app import app, api, jwt
from app.models import Commands, Macros, Beacons, BeaconHistory
from app.operations import Task
from flask import Flask, request, g
from flask_restful import Api, Resource, reqparse
from mongoengine.queryset.visitor import Q
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)

from bson.json_util import dumps as loadbson


class APIBeacons(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('platform', type=str, required=False, location='args', default="")
        self.parser.add_argument('search', type=str, required=False, location='args', default="")

    def get(self):
        args = self.parser.parse_args()
        pipeline = [{"$lookup":{"from":"beacon_history","let":{"beacon_id":"$beacon_id"},"as":"output","pipeline":[
            {"$match":{"$expr":{"$eq":["$$beacon_id","$beacon_id"]}}},{"$sort":{"timestamp":-1}},{"$limit":1}]}},
            {"$unwind":"$output"},{"$addFields":{"statecheck":{"$add":["$output.timestamp",{"$multiply":["$timer",1500]}]}}},
            {"$addFields":{"state":{"$cond":{"if":{"$gte":["$statecheck","$output.timestamp"]},"then":"Offline","else":"Online"}}}}]

        get_beacons = Beacons.objects(Q(platform__contains=args['platform']) & (
            Q(username__contains=args['search']) | Q(hostname__contains=args['search'])
            )).aggregate(*pipeline)

        results = json.loads(loadbson(get_beacons))

        return results

api.add_resource(APIBeacons, '/api/v1/agents')


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


