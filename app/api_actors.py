from app import app, api, jwt
from app.models import Actors, CommandMapping
from flask import Flask, request, g
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)
from bson.json_util import dumps as loadbson
import json


class APIActors(Resource):
    decorators = [jwt_required]

    def get(self):
        mitre_actors = Actors.objects().distinct('name')
        return mitre_actors

api.add_resource(APIActors, '/api/v1/mitre/actors')


class APIActor(Resource):
    decorators = [jwt_required]

    def get(self, actor_name):
        mitre_actor = Actors.objects.get(name=actor_name)
        json_object = json.loads(mitre_actor.to_json())
        return json_object

api.add_resource(APIActor, '/api/v1/mitre/actors/<string:actor_name>')


class APIActorsMapping(Resource):
    decorators = [jwt_required]

    def get(self):
        mitre_actors = CommandMapping.objects().distinct('actors.name')
        return mitre_actors

api.add_resource(APIActorsMapping, '/api/v1/mapping/actors')


class APIActorMapping(Resource):
    decorators = []

    def get(self, actor_name):
        actor_objects = CommandMapping.objects(actors__name=actor_name)
        json_object = json.loads(actor_objects.to_json())
        return json_object

api.add_resource(APIActorMapping, '/api/v1/mapping/actors/<string:actor_name>')

