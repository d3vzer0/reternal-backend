from database.models import Validations
from app import api, celery
from app.utils.depends import validate_worker
from fastapi import Depends, Body
from app.schemas.validations import ValidationsIn, ValidationsOut
from bson.json_util import dumps
from typing import List, Dict
import json


async def dynamic_search(phase: str = None, integration: str = 'Splunk', technique: str = None,
    l1usecase: str = None, l2usecase: str = None, datasource: str = None):
    query = { 'integration': integration,
        'technique_name': technique, 
        'kill_chain_phases': phase, 
        'magma__l1_usecase_name': l1usecase, 
        'magma__l2_usecase_name': l2usecase,
        'data_sources__contains': datasource
    }
    return {arg: value for arg, value in query.items() if value is not None}

@api.post('/api/v1/validations', response_model=ValidationsOut)
async def create_validations(validation: ValidationsIn):
    create_validation = Validations.create(**validation.dict())
    return create_validation

@api.get('/api/v1/validations/integrations', response_model=List[str])
async def get_validation_integrations():
    ''' Get all unique integrations for available queries '''
    unique_integrations = Validations.objects().distinct('integration')
    return unique_integrations

@api.get('/api/v1/validations/phases', response_model=List[str])
async def get_validation_phases(query: dict = Depends(dynamic_search)):
    ''' Get all unique phases for available queries '''
    unique_phases = Validations.objects(**query).distinct('kill_chain_phases')
    return unique_phases

@api.get('/api/v1/validations/datasources')
async def get_validation_datasources(query: dict = Depends(dynamic_search)):
    ''' Get all unique datasources for available queries '''
    unique_datasources = Validations.objects(**query).distinct('data_sources')
    return unique_datasources

@api.get('/api/v1/validations/techniques', response_model=List[str])
async def get_validation_techniques(query: dict = Depends(dynamic_search)):
    ''' Get all unique phases for available queries '''
    unique_phases = Validations.objects(**query).distinct('technique_name')
    return unique_phases

@api.get('/api/v1/validations/l1usecases', response_model=List[str])
async def get_l1_usecases(query: dict = Depends(dynamic_search)):
    ''' Get all unique L1 usecases for available queries '''
    unique_usecases = Validations.objects(**query).distinct('magma.l1_usecase_name')
    return unique_usecases

@api.get('/api/v1/validations/l2usecases', response_model=List[str])
async def get_l2_usecases(query: dict = Depends(dynamic_search)):
    ''' Get all unique L2 usecases for available queries '''
    unique_usecases = Validations.objects(**query).distinct('magma.l2_usecase_name')
    return unique_usecases

@api.get('/api/v1/validations', response_model=List[ValidationsOut])
async def get_validations(query: dict = Depends(dynamic_search)):
    ''' Get all Validations that are mapped to ATTCK and have a query available '''
    validation_objects = Validations.objects(**query)
    result = json.loads(validation_objects.to_json())
    return result
