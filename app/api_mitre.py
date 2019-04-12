from app import app, api, jwt
from app.models import Techniques, Actors
from flask import Flask, request, g
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)
from bson.json_util import dumps
import json


class APITechniquesAggregate(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.args = reqparse.RequestParser()
        self.args.add_argument('name', location='args', help='Technique_name', default='')
        self.args.add_argument('phase', location='args', help='Phase', default='')
        self.args.add_argument('platform', location='args', help='Platform', default='Windows')
        self.args.add_argument('actor', location='args', help='Actor', default='')
  
    def get(self):
        pipeline = [{"$unwind":"$kill_chain_phases"},
            {'$group':{ '_id':{'kill_chain_phases':'$kill_chain_phases'},
            'techniques':{'$push': {'name':'$name', 'technique_id':'$technique_id'}}}}]

        args = self.args.parse_args()
        mitre_objects = Techniques.objects(platforms__contains=args['platform'],
            name__contains=args['name'], actors__name__contains=args.actor, kill_chain_phases__contains=args['phase']).only('name',
            'kill_chain_phases', 'platforms', 'actors').aggregate(*pipeline)
        json_object = json.loads(dumps(mitre_objects))
        return json_object

api.add_resource(APITechniquesAggregate, '/api/v1/mitre/techniques')


class APITechniqueDetails(Resource):
    decorators = [jwt_required]

    def get(self, technique_id):
        mitre_technique = Techniques.objects.get(technique_id=technique_id)
        json_object = json.loads(mitre_technique.to_json())
        return json_object

api.add_resource(APITechniqueDetails, '/api/v1/mitre/technique/<string:technique_id>')


class APIActors(Resource):
    decorators = [jwt_required]

    def get(self):
        mitre_actors = Actors.objects().distinct('name')
        return mitre_actors

api.add_resource(APIActors, '/api/v1/mitre/actors')


class APITechniquePhases(Resource):
    decorators = [jwt_required]

    def get(self):
        mitre_phases = Techniques.objects().distinct('kill_chain_phases')
        return mitre_phases

api.add_resource(APITechniquePhases, '/api/v1/mitre/phases')

class APITechniqueDatasources(Resource):
    decorators = [jwt_required]

    def get(self):
        mitre_datasources = Techniques.objects().distinct('data_sources')
        return mitre_datasources

api.add_resource(APITechniqueDatasources, '/api/v1/mitre/datasources')

