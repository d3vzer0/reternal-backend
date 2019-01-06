from app import app, api, celery, jwt
from app.models import MitreCommands
from flask import Flask, request, g
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)
from bson.json_util import dumps
import json


class APIMapping(Resource):
    decorators = []

    def __init__(self):
        self.args = reqparse.RequestParser()
        self.args.add_argument('name', location='args', help='Technique_name', default="")
        self.args.add_argument('phase', location='args', help='Phase', default="")
        self.args.add_argument('platform', location='args', help='Platform', default="Windows")
  
    def get(self):
        args = self.args.parse_args()
        pipeline = [{'$group':{'_id':{'kill_chain_phase':'$kill_chain_phase'},'techniques':{'$push': 
            {'_id':'$_id', 'technique_id':'$technique_id', 'metta_id':'$metta_id', 'name':'$name'}}}}]
        mitre_objects = MitreCommands.objects(platform__contains=args['platform'],
            external_id__contains=args['name'], kill_chain_phase__contains=args['phase']).aggregate(*pipeline)
        json_object = json.loads(dumps(mitre_objects))
        return json_object

api.add_resource(APIMapping, '/api/v1/mitre/mapping')


class APIMappingDetails(Resource):
    decorators = []

    def get(self, map_id):
        mitre_technique = MitreCommands.objects.get(id=map_id)
        json_object = json.loads(mitre_technique.to_json())
        return json_object

api.add_resource(APIMappingDetails, '/api/v1/mitre/mapping/<string:map_id>')



