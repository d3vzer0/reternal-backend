from fastapi import Depends, APIRouter, Security
from app.utils.depends import validate_token
from app.database.models.commandmapping import CommandMapping
from app.schemas.mapping import MappingOut, MappingTechniquesOut, MappingTechniquesIn
from bson.json_util import dumps
from typing import List, Dict
import json

QUERYMAPPING = {
    'technique': 'techniques.references.0.external_id',
    'platform': 'platform',
    'integration': 'integration',
    'technique_name': 'techniques.name',
    'phase': 'techniques.kill_chain_phases',
    'actor': 'actors.name',
    'data_source': 'techniques.data_sources',
    'name': 'name'
}

router = APIRouter() 


async def dynamic_search(search: str = None, phase: str = None, platform: str = 'Windows',
    technique: str = None, actor: str = None, integration: str = None):
    query = {
        'name__contains': search,
        'techniques__kill_chain_phases': phase,
        'platform': platform,
        'techniques__name': technique, 
        'actors__name': actor,
        'integration': integration
    }
    return {arg: value for arg, value in query.items() if value != None and value != ''}

async def parse_list(fields: str) -> List:
    return fields.split(',')


@router.post('/mapping', response_model=MappingOut, dependencies=[Security(validate_token, scopes=['write:content'])])
async def create_mapping(mapping: MappingTechniquesIn):
    create_mapping = CommandMapping.objects(name=mapping.name).upsert_one(**mapping.dict())
    return create_mapping.to_dict()


@router.get('/mapping/distinct', response_model=Dict[str, List[str]], dependencies=[Security(validate_token)])
async def get_sigma_distinct(query: dict = Depends(dynamic_search), fields: List[str] = Depends(parse_list)):
    mapped_techniques = CommandMapping.objects(**query)
    filtered_fields = [field for field in fields if field in QUERYMAPPING]
    distinct_values = {field: mapped_techniques.distinct(QUERYMAPPING[field]) for field in filtered_fields}
    return distinct_values


@router.get('/mapping/techniques', response_model=MappingTechniquesOut, dependencies=[Security(validate_token)])
async def get_mapped_techniques(query: dict = Depends(dynamic_search), skip: int = 0, limit: int = 10):
    ''' Get all C2 tasks that are mapped to ATTCK '''
    mapped_techniques = CommandMapping.objects(**query)
    result = {'total': mapped_techniques.count(), 'results': json.loads(mapped_techniques[skip:limit].to_json())}
    return result


@router.get('/mapping/techniques/distinct', response_model=List[str], dependencies=[Security(validate_token)])
async def get_mapped_techniques():
    ''' Get all C2 tasks that are mapped to ATTCK '''
    mapped_techniques = CommandMapping.objects().distinct('name')
    return mapped_techniques


@router.get('/mitre/mapping/{mapping_id}', dependencies=[Security(validate_token)])
async def get_mapping(mapping_id: str):
    ''' Get specific mapping object by id '''
    mitre_technique = json.loads(CommandMapping.objects.get(id=mapping_id).to_json())
    return mitre_technique
