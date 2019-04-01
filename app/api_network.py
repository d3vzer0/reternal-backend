from app import app, api, jwt
from app.models import BeaconHistory
from flask import Flask, request, g
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)
from bson.json_util import dumps
import json

class APINetwork(Resource):
    decorators = []

    def get(self):
        pipeline = [{'$group': {'_id':{'beacon_id':'$beacon_id'},'agents': {'$push': '$$ROOT'}}},
                    {'$group': {'_id':{'remote_ip':'$remote_ip'},'agents': {'$push': '$$ROOT'}}}]
        network_graph = BeaconHistory.objects().aggregate(*pipeline)
        result = json.loads(dumps(network_graph))
        return result


api.add_resource(APINetwork, '/api/v1/network')
