from fastapi import APIRouter, Security
from app.utils.depends import validate_token
# from app.database.graphs.neo4j import Technique as TGraph, Reference
from app.database.models.techniques import Techniques
from app.database.models.actors import Actors
from app.database.models.coverage import Coverage
from app.schemas.coverage import CoverageOut, CoverageIn
from app.schemas.attck import AttckTechniquesOut, AttckAggPhasesOut, AttckActorOut
from app.schemas.techniques import CreateTechniquesIn, CreateTechniquesOut
from app.schemas.actors import CreateActorIn, CreateActorOut
from bson.json_util import dumps
from typing import List, Dict
import json

router = APIRouter()


@router.post('/mitre/techniques', response_model=CreateTechniquesOut, dependencies=[Security(validate_token, scopes=['write:content'])])
async def create_technique(techniques: CreateTechniquesIn):
    ''' Create new MITRE ATTCK technique '''
    technique = Techniques.objects(technique_id=techniques.technique_id).upsert_one(**techniques.dict())
    # new_technique = technique.upsert_one(**techniques.dict())
    technique.update_sigma()
    # technique.update_actors()
    # technique.update_commands()
    return technique.to_dict()


@router.get('/mitre/techniques', response_model=List[str], dependencies=[Security(validate_token)])
async def get_techniques(technique_id: str):
    ''' Get the unique ATTCK techniques '''
    mitre_techniques = Techniques.objects().distinct('name')
    json_object = json.loads(mitre_techniques.to_json())
    return json_object


@router.get('/mitre/technique/{technique_id}', response_model=AttckTechniquesOut, dependencies=[Security(validate_token)])
async def get_technique(technique_id: str):
    ''' Get technique details by technique ID '''
    mitre_technique = Techniques.objects.get(technique_id=technique_id)
    json_object = json.loads(mitre_technique.to_json())
    return json_object


@router.get('/mitre/phases', response_model=List[str], dependencies=[Security(validate_token)])
async def get_phases():
    ''' Get the unique ATTCK kill chain phases '''
    mitre_phases = Techniques.objects().distinct('kill_chain_phases')
    return mitre_phases
    

@router.get('/mitre/datasources', response_model=List[str], dependencies=[Security(validate_token)])
async def get_datasources():
    ''' Get the unique datasources '''
    mitre_datasources = Techniques.objects().distinct('data_sources')
    return [ds for ds in mitre_datasources if ds]


@router.post('/mitre/actors', response_model=CreateActorOut, dependencies=[Security(validate_token)])
async def create_actor(actor: CreateActorIn):
    ''' Create new MITRE ATTCK actor '''
    new_actor = Actors.objects(actor_id=actor.actor_id).upsert_one(**actor.dict())
    new_actor.update_techniques()
    new_actor.update_sigma()
    new_actor.update_commands()
    return new_actor.to_dict()


@router.get('/mitre/actors', response_model=List[str], dependencies=[Security(validate_token)])
async def get_actors():
    ''' Get the unique ATTCK actors '''
    mitre_actors = Actors.objects().distinct('name')
    return mitre_actors


@router.get('/mitre/actor/{actor_name}', response_model=AttckActorOut, dependencies=[Security(validate_token)])
async def get_actor(actor_name: str):
    ''' Get the actor details by actor name '''
    mitre_actor = Actors.objects.get(name=actor_name)
    json_object = json.loads(mitre_actor.to_json())
    return json_object


@router.get('/products/coverage', response_model=CoverageOut, dependencies=[Security(validate_token)])
async def get_products(datasource: str):
    ''' Get configured products from coverage mapping '''
    coverage_products = Coverage.objects.get(data_source_name__iexact=datasource)
    json_object = json.loads(coverage_products.to_json())
    return json_object


@router.get('/mitre/coverage', response_model=List[CoverageOut], dependencies=[Security(validate_token)])
async def get_coverages():
    ''' Get the current datasources coverage documents'''
    mitre_coverage = Coverage.objects()
    json_object = json.loads(mitre_coverage.to_json())
    return json_object


@router.post('/mitre/coverage', dependencies=[Security(validate_token, scopes=['write:content'])])
async def set_coverage(coverage_data: CoverageIn):
    ''' Update or create a new datasource coverage document '''
    modify_coverage = Coverage.create(**coverage_data.dict())
    return modify_coverage


@router.delete('/mitre/coverage/{coverage_id}', response_model=Dict[str, str], dependencies=[Security(validate_token, scopes=['write:content'])])
async def delete_coverage(coverage_id: str):
    ''' Delete the current datasources coverage document'''
    delete_coverage = Coverage.delete(coverage_id)
    return delete_coverage


@router.get('/mitre/coverage/{coverage_id}', response_model=CoverageOut, dependencies=[Security(validate_token)])
async def get_coverage(coverage_id: str):
    ''' Get the current datasources coverage document'''
    mitre_coverage = Coverage.objects.get(id=coverage_id)
    json_object = json.loads(mitre_coverage.to_json())
    return json_object


@router.get('/mitre/aggregate/by_phase', response_model=List[AttckAggPhasesOut], dependencies=[Security(validate_token)])
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
