from app import api, celery
from app.utils.depends import validate_worker
from fastapi import Depends, Body
from database.models import Techniques, Actors, CommandMapping
from app.schemas.mapping import MappingCountOut, MappingTechniquesOut, MappingTechniquesIn
from bson.json_util import dumps
from typing import List, Dict
import json


async def dynamic_search(phase: str = None, platform: str = 'Windows',
    technique: str = None, actor: str = None, integration: str = None):
    query = {
        'kill_chain_phase': phase,
        'platform': platform,
        'technique_name': technique, 
        'actors__name': actor,
        'integration': integration
    }
    return {arg: value for arg, value in query.items() if value is not None}

@api.post('/api/v1/mapping', response_model=List[MappingTechniquesOut])
async def create_mapping(mapping: MappingTechniquesIn):
    create_mapping = CommandMapping.create(**mapping.dict())
    return create_mapping

@api.get('/api/v1/mapping/phases', response_model=List[str])
async def get_mapped_phases(query: dict = Depends(dynamic_search)):
    ''' Get all unique phases for C2 tasks that have been maped to ATTCK '''
    unique_phases = CommandMapping.objects(**query).distinct('kill_chain_phase')
    return unique_phases

# @api.get('/api/v1/mapping/techniques/distinct', response_model=List[str])
# async def get_techniques(distinct: str, phase: str = '', platform: str = 'Windows',
#     technique: str = '', actor: str = ''):
#     ''' Get all unique techniques that have been maped to ATTCK '''
#     techniques_objects = CommandMapping.objects(platform__contains=platform,
#             technique_name__contains=technique, kill_chain_phase__contains=phase,
#             actors__name__contains=actor)
#     result = techniques_objects.distinct(field=distinct)
#     return result

@api.get('/api/v1/mapping/techniques', response_model=List[MappingTechniquesOut])
async def get_mapped_techniques(query: dict = Depends(dynamic_search)):
    ''' Get all C2 tasks that are mapped to ATTCK '''
    techniques_objects = json.loads(CommandMapping.objects(**query).to_json())
    return techniques_objects

@api.get('/api/v1/mitre/mapping/{mapping_id}')
async def get_mapping(mapping_id: str):
    ''' Get specific mapping object by id '''
    mitre_technique = json.loads(CommandMapping.objects.get(id=mapping_id).to_json())
    return mitre_technique

@api.get('/api/v1/mapping/actors', response_model=List[str])
async def get_actors_mapping(query: dict = Depends(dynamic_search)):
    ''' Get all unique actors for C2 tasks that have been maped to ATTCK '''
    get_unique_actors = CommandMapping.objects(**query).distinct('actors.name')
    return get_unique_actors

@api.get('/api/v1/mapping/platforms', response_model=List[str])
async def get_platforms_mapping(query: dict = Depends(dynamic_search)):
    ''' Get all unique platforms for C2 tasks that have been maped to ATTCK '''
    get_unique_platforms = CommandMapping.objects(**query).distinct('platform')
    return get_unique_platforms

@api.get('/api/v1/mapping/count', response_model=List[MappingCountOut])
async def get_mapping_count(by: str = 'phase'):
    ''' Get count of currently mapped techniques '''
    mapping = {'phase': '$kill_chain_phase', 'platform':'$platform'}
    pipeline = [{"$group": 
        { "_id": mapping.get(by, '$kill_chain_phase'), "count":{ "$sum": 1 } }
    }]
    get_techniques_by_phase = CommandMapping.objects().aggregate(pipeline)
    result = json.loads(dumps(get_techniques_by_phase))
    return result
