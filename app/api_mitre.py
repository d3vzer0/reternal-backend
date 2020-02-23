from app import api, celery
from app.utils.depends import validate_worker
from fastapi import Depends, Body
from app.database.models import Techniques, Actors
from bson.json_util import dumps
import json


@api.get('/api/v1/mitre/by_phase')
async def aggregated_techniques(name: str = '', phase: str = '', platform: str = 'Windows', actor: str = ''):
    pipeline = [{"$unwind":"$kill_chain_phases"},
        {'$group':{ '_id':{'kill_chain_phases':'$kill_chain_phases'},
        'techniques':{'$push': {'name':'$name', 'technique_id':'$technique_id'}}}}]
    mitre_objects = Techniques.objects(platforms__contains=platform,
        name__contains=name, actors__name__contains=actor, kill_chain_phases__contains=phase).only('name',
        'kill_chain_phases', 'platforms', 'actors').aggregate(*pipeline)
    json_object = json.loads(dumps(mitre_objects))
    return json_object


@api.get('/api/v1/mitre/techniques')
async def get_technique(technique_id: str):
    mitre_techniques = Techniques.objects().distinct('name')
    json_object = json.loads(mitre_techniques.to_json())
    return json_object


@api.get('/api/v1/mitre/technique/{technique_id}')
async def get_technique(technique_id: str):
    mitre_technique = Techniques.objects.get(technique_id=technique_id)
    json_object = json.loads(mitre_technique.to_json())
    return json_object


@api.get('/api/v1/mitre/phases')
async def get_phases():
    mitre_phases = Techniques.objects().distinct('kill_chain_phases')
    return mitre_phases
    

@api.get('/api/v1/mitre/datasources')
async def get_datasources():
    mitre_datasources = Techniques.objects().distinct('data_sources')
    return mitre_datasources


@api.get('/api/v1/mitre/actors')
async def get_actors():
    mitre_actors = Actors.objects().distinct('name')
    return mitre_actors


@api.get('/api/v1/mitre/actor/{actor_name}')
async def get_actor(actor_name: str):
    mitre_actor = Actors.objects.get(name=actor_name)
    json_object = json.loads(mitre_actor.to_json())
    return json_object
