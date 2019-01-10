from app import app, api, celery, jwt
from app.models import Macros, Beacons, BeaconHistory
from app.operations import Macro
from app.validators import Existance
from flask import Flask, request, g
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)
from bson.json_util import dumps as bsonload
import json
from datetime import datetime, timedelta

class APIStats(Resource):
    decorators = [jwt_required]
    def get(self, stats_type):
        if stats_type == "pulse":
            pipeline = [{ "$group":{ "_id": { 
                "year": {"$year":"$timestamp" },
                "month": {"$month":"$timestamp" },
                "day": {"$dayOfMonth":"$timestamp" }, 
                "hour":{"$hour":"$timestamp" }, 
                }, 
                "total": {"$sum": 1} }},{ "$sort" : { "_id.month" : -1, "_id.day" : -1, "_id.hour" : -1 } }]
            last_week = datetime.today() - timedelta(days=7)
            stats = json.loads(bsonload(BeaconHistory.objects(timestamp__gte=last_week).order_by('-timestamp').aggregate(*pipeline)))

        elif stats_type == "platforms":
            pipeline = [{"$group": {"_id": "$platform", "count": { "$sum":1} }}]
            stats = json.loads(bsonload(Beacons.objects.aggregate(*pipeline)))

        elif stats_type == "agents":
            pipeline = [{"$count":"beacon_count"}]
            stats = json.loads(bsonload(Beacons.objects.aggregate(*pipeline)))

        elif stats_type == "new":
            pipeline = [{"$count":"beacon_count"}]
            this_week = datetime.today() - timedelta(days=7)
            last_week = datetime.today() - timedelta(days=14)
            this_week = json.loads(bsonload(Beacons.objects(timestamp__gte=this_week).aggregate(*pipeline)))
            last_week = json.loads(bsonload(Beacons.objects(timestamp__gte=last_week, timestamp__lte=this_week).aggregate(*pipeline)))
            stats = {"this_week":this_week, "last_week":last_week}

        else:
            stats = {"result":"failed", "data":"Wrong stats type"}

        return stats


api.add_resource(APIStats, '/api/v1/stats/<string:stats_type>')
