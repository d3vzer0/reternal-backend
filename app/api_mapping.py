from app.database.models import CommandMapping
from app import api, celery
from app.utils.depends import validate_worker
from app.utils.mapping import Mapping
from fastapi import Depends, Body
from app.database.models import Techniques, Actors
from bson.json_util import dumps
import json

@api.post('/api/v1/mapping/update')
async def update_mapping():
    ''' Sync the mapping objects that relate commands to MITRE ATTCK '''
    sync_techniques = Mapping().load()

@api.get('/api/v1/mapping/techniques/distinct')
async def get_techniques(distinct: str, phase: str = '', platform: str = 'Windows',
    technique: str = '', actor: str = ''):
    ''' Get all unique techniques that have been maped to ATTCK '''
    techniques_objects = CommandMapping.objects(platform__contains=platform,
            technique_name__contains=technique, kill_chain_phase__contains=phase,
            actors__name__contains=actor)
    result = techniques_objects.distinct(field=distinct)
    return result

@api.get('/api/v1/mapping/techniques')
async def get_technique(phase: str = '', platform: str = 'Windows', actor: str = '', integration: str = ''):
    ''' Get all techniques that are mapped to ATTCK and match the provided filter options '''
    techniques_objects = CommandMapping.objects(platform=platform, commands__integration__contains=integration,
            kill_chain_phase__contains=phase, actors__name__contains=actor)
    result = json.loads(techniques_objects.to_json())
    return result

@api.get('/api/v1/mitre/mapping/{mapping_id}')
async def get_mapping(mapping_id: str):
    ''' Get specific mapping object by id '''
    mitre_technique = CommandMapping.objects.get(id=mapping_id)
    json_object = json.loads(mitre_technique.to_json())
    return json_object

@api.get('/api/v1/mapping/actors')
async def get_actors_mapping():
    ''' Get all unique actors '''
    mitre_actors = CommandMapping.objects().distinct('actors.name')
    return mitre_actors

@api.get('/api/v1/mapping/actor/{actor_name}')
async def get_actor_mapping(actor_name: str):
    ''' Get actor details by actor name '''
    actor_objects = CommandMapping.objects(actors__name=actor_name)
    json_object = json.loads(actor_objects.to_json())
    return json_object

@api.get('/api/v1/mapping/count')
async def get_mapping_count(by: str = 'phase'):
    ''' Get count of currently mapped techniques '''
    mapping = {'phase': '$kill_chain_phase', 'platform':'$platform'}
    pipeline = [{"$group" : {"_id": mapping.get(by, '$kill_chain_phase'), "count":{"$sum":1}}}]
    get_techniques_by_phase = CommandMapping.objects().aggregate(pipeline)
    result = json.loads(dumps(get_techniques_by_phase))
    return result
