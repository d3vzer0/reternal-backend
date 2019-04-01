from app import app, api, jwt
from app.models import CommandMapping
from flask import Flask, request, g
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)
from bson.json_util import dumps
import json


class APIMapping(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.args = reqparse.RequestParser()
        self.args.add_argument('name', location='args', help='Technique_name', default='')
        self.args.add_argument('phase', location='args', help='Phase', default='')
        self.args.add_argument('platform', location='args', help='Platform', default="Windows")
        self.args.add_argument('technique', location='args', help='Technique', default='')
        self.args.add_argument('distinct', location='args', help='Distinct', required=False,
            choices=('technique_name', 'kill_chain_phase', 'name'))

    def get(self):
        args = self.args.parse_args()
        mitre_objects = CommandMapping.objects(platform__contains=args['platform'],
            name__contains=args['name'], technique_name__contains=args['technique'], 
            kill_chain_phase__contains=args['phase'])
        result = mitre_objects.distinct(field=args.distinct) if args.distinct else json.loads(mitre_objects.to_json())
        return result

api.add_resource(APIMapping, '/api/v1/mapping')



class APIMappingDetails(Resource):
    decorators = [jwt_required]

    def get(self, map_id):
        mitre_technique = CommandMapping.objects.get(id=map_id)
        json_object = json.loads(mitre_technique.to_json())
        return json_object

api.add_resource(APIMappingDetails, '/api/v1/mitre/mapping/<string:map_id>')



