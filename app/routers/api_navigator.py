from app import app, api, jwt
from app.models import Tasks
from flask import Flask, request, g
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)
import json

class APINavigatorTasks(Resource):
    decorators = []

    def __init__(self, layer_file='app/mitre/reternal-layer.json'):
        self.layer_file = layer_file

    def get(self):
        with open(self.layer_file, 'r') as layer_content:
            layer_json = json.loads(layer_content.read())

        pipeline = [
            {'$unwind': '$commands' },
            {'$lookup': {'from':'command_mapping','localField':'commands.reference', 'foreignField':'_id', 'as':'metadata'}},
            {'$lookup': {'from':'beacons','localField':'beacon_id', 'foreignField':'beacon_id', 'as':'beacon_details'}},
            {'$unwind': {'path':'$metadata', 'preserveNullAndEmptyArrays':True}},
            {'$unwind': {'path':'$beacon_details', 'preserveNullAndEmptyArrays':True}},
            {'$group':{'_id':{'technique':'$metadata.external_id'},'agents':{'$push': {'agent':'$beacon_details', 'technique_id':'$technique_id'}}}}]

        tasks = Tasks.objects(commands__type__="Mitre").aggregate(*pipeline)
        for task in tasks:
            task_data = {
                'techniqueID':task['_id']['technique'], 
                'comment': 'This task has been executed via Reternal', 'color': '#fd8d3c'}
            task_data['metadata'] = [{'value':agent['agent']['beacon_id'], 'name': agent['agent']['hostname']} for agent in task['agents']]
            layer_json['techniques'].append(task_data)

        result = json.dumps(layer_json)
        return layer_json

api.add_resource(APINavigatorTasks, '/api/v1/navigator/tasks')