from app import app, api, celery, jwt
from app.models import Mitre
from flask import Flask, request, g
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)

class APIMitre(Resource):
    decorators = []

    def get(self):
        pipeline = [
                {"$unwind" : "$platforms"},
                {"$unwind":"$kill_chain_phases"},
                {'$group':{
                    '_id':{'kill_chain_phases':'$kill_chain_phases', 'platforms':'$platforms'},
                    'techniques':{'$push': '$$ROOT'}
                    }
                }
            ]

        mitre_objects = Mitre.objects.aggregate(*pipeline)
        results = []
        for objects in mitre_objects:
            object_item = {'kill_chain_phase':objects['_id']['kill_chain_phases'], 'platform':objects['_id']['platforms'], 'techniques':[]}
            for technique in objects['techniques']:
                technique_details = {'name':technique['name'],
                    'technique_id':technique['technique_id'], 
                    'references':technique['references'], 
                    'commands':[]
                }
                for command in technique['commands']:
                    mitre_tasks = {'command':str(command['command']), 'input':command['taskInput']}
                    technique_details['commands'].append(mitre_tasks)
                object_item['techniques'].append(technique_details)
            results.append(object_item)

        return result


api.add_resource(APIMitre, '/api/v1/mitre/aggregate')
