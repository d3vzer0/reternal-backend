from app import api, celery
from app.utils.depends import validate_worker
from fastapi import Depends, Body, BackgroundTasks
from database.models import Techniques, Actors, Coverage
from app.schemas.datasources import DatasourcesOut
from app.schemas.coverage import CoverageOut, CoverageIn
from app.schemas.attck import AttckTechniquesOut, AttckAggPhasesOut, AttckActorOut
from app.schemas.techniques import CreateTechniquesIn, CreateTechniquesOut
from app.schemas.actors import CreateActorIn, CreateActorOut
from bson.json_util import dumps
from typing import List, Dict
import json


@api.post('/api/v1/mitre/techniques', response_model=CreateTechniquesOut)
async def create_technique(techniques: CreateTechniquesIn):
    ''' Create new MITRE ATTCK technique '''
    create_technique = Techniques.create(**techniques.dict())
    return create_technique

@api.get('/api/v1/mitre/techniques', response_model=List[str])
async def get_techniques(technique_id: str):
    ''' Get the unique ATTCK techniques '''
    mitre_techniques = Techniques.objects().distinct('name')
    json_object = json.loads(mitre_techniques.to_json())
    return json_object


@api.get('/api/v1/mitre/technique/{technique_id}', response_model=AttckTechniquesOut)
async def get_technique(technique_id: str):
    ''' Get technique details by technique ID '''
    mitre_technique = Techniques.objects.get(technique_id=technique_id)
    json_object = json.loads(mitre_technique.to_json())
    return json_object


@api.get('/api/v1/mitre/phases', response_model=List[str])
async def get_phases():
    ''' Get the unique ATTCK kill chain phases '''
    mitre_phases = Techniques.objects().distinct('kill_chain_phases')
    return mitre_phases
    

@api.get('/api/v1/mitre/datasources', response_model=List[str])
async def get_datasources():
    ''' Get the unique datasources '''
    mitre_datasources = Techniques.objects().distinct('data_sources')
    return [ds for ds in mitre_datasources if ds]


@api.post('/api/v1/mitre/actors', response_model=CreateActorOut)
async def create_actor(actor: CreateActorIn):
    ''' Create new MITRE ATTCK actor '''
    create_actor = Actors.create(**actor.dict())
    return create_actor


@api.get('/api/v1/mitre/actors', response_model=List[str])
async def get_actors():
    ''' Get the unique ATTCK actors '''
    mitre_actors = Actors.objects().distinct('name')
    return mitre_actors


@api.get('/api/v1/mitre/actor/{actor_name}', response_model=AttckActorOut)
async def get_actor(actor_name: str):
    ''' Get the actor details by actor name '''
    mitre_actor = Actors.objects.get(name=actor_name)
    json_object = json.loads(mitre_actor.to_json())
    return json_object


@api.get('/api/v1/mitre/coverage', response_model=List[CoverageOut])
async def get_coverages():
    ''' Get the current datasources coverage documents'''
    mitre_coverage = Coverage.objects()
    json_object = json.loads(mitre_coverage.to_json())
    return json_object


@api.post('/api/v1/mitre/coverage')
async def set_coverage(coverage_data: CoverageIn):
    ''' Update or create a new datasource coverage document '''
    modify_coverage = Coverage.create(**coverage_data.dict())
    return modify_coverage


@api.delete('/api/v1/mitre/coverage/{coverage_id}', response_model=Dict[str, str])
async def delete_coverage(coverage_id: str):
    ''' Delete the current datasources coverage document'''
    delete_coverage = Coverage.delete(coverage_id)
    return delete_coverage


@api.get('/api/v1/mitre/coverage/{coverage_id}', response_model=CoverageOut)
async def get_coverage(coverage_id: str):
    ''' Get the current datasources coverage document'''
    mitre_coverage = Coverage.objects.get(id=coverage_id)
    json_object = json.loads(mitre_coverage.to_json())
    return json_object


@api.get('/api/v1/mitre/aggregate/by_phase', response_model=List[AttckAggPhasesOut])
async def aggregated_techniques(name: str = '', phase: str = '', platform: str = 'Windows', actor: str = ''):
    ''' Get all of the ATTCK techniques grouped by attack phase '''
    pipeline = [
        {"$unwind":"$kill_chain_phases"},
        {'$group': { '_id': {
            'kill_chain_phases':'$kill_chain_phases'},
            'techniques': { '$push':
                {'name':'$name', 'technique_id':'$technique_id', 'data_sources': '$data_sources',
                    'data_sources_available': '$data_sources_available' } }
            }
        }
    ]
    mitre_objects = Techniques.objects(platforms__contains=platform,
        name__contains=name, actors__name__contains=actor, kill_chain_phases__contains=phase).only('name',
        'kill_chain_phases', 'platforms', 'actors').aggregate(*pipeline)
    json_object = json.loads(dumps(mitre_objects))
    return json_object
