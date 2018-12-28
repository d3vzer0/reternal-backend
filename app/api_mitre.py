from app import app, api, celery, jwt
from app.models import Mitre
from flask import Flask, request, g
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)
from bson.json_util import dumps
import json

class APIMitreAggregate(Resource):
    decorators = []

    def __init__(self):
        self.args = reqparse.RequestParser()
        self.args.add_argument('name', location='args', help='Technique_name', default="")
        self.args.add_argument('phase', location='args', help='Phase', default="")
        self.args.add_argument('platform', location='args', help='Platform', default="Windows")
  
    def get(self):
        pipeline = [{"$unwind":"$kill_chain_phases"},
                    {'$group':{
                        '_id':{'kill_chain_phases':'$kill_chain_phases'},
                        'techniques':{'$push': {'name':'$name', 'technique_id':'$technique_id'}}
                        }
                     }]
        args = self.args.parse_args()
        mitre_objects = Mitre.objects(platforms__contains=args['platform'],
            name__contains=args['name'], kill_chain_phases__contains=args['phase']).only('name',
            'kill_chain_phases', 'platforms').aggregate(*pipeline)
        json_object = json.loads(dumps(mitre_objects))
        return json_object

api.add_resource(APIMitreAggregate, '/api/v1/mitre/aggregate')


class APIMitreDetails(Resource):
    decorators = []

    def get(self, technique_id):
        mitre_technique = Mitre.objects.get(technique_id=technique_id)
        json_object = json.loads(mitre_technique.to_json())
        return json_object

api.add_resource(APIMitreDetails, '/api/v1/mitre/technique/<string:technique_id>')
