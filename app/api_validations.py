from app.database.models import Validations
from app import api, celery
from app.utils.depends import validate_worker
from fastapi import Depends, Body
from app.schemas.validations import ValidationsIn, ValidationsOut
from bson.json_util import dumps
from typing import List, Dict
import json


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
async def get_validation_phases(integration: str, technique: str = ''):
    ''' Get all unique phases for available queries '''
    unique_phases = Validations.objects(integration=integration, technique_name__contains=technique).distinct('kill_chain_phases')
    return unique_phases

@api.get('/api/v1/validations/techniques', response_model=List[str])
async def get_validation_techniques(integration: str):
    ''' Get all unique phases for available queries '''
    unique_phases = Validations.objects(integration=integration).distinct('technique_name')
    return unique_phases

@api.get('/api/v1/validations/l1usecases', response_model=List[str])
async def get_l1_usecases(integration: str):
    ''' Get all unique L1 usecases for available queries '''
    unique_usecases = Validations.objects(integration=integration).distinct('magma.l1_usecase_name')
    return unique_usecases

@api.get('/api/v1/validations/l2usecases', response_model=List[str])
async def get_l1_usecases(integration: str):
    ''' Get all unique L2 usecases for available queries '''
    unique_usecases = Validations.objects(integration=integration).distinct('magma.l2_usecase_name')
    return unique_usecases

@api.get('/api/v1/validations', response_model=List[ValidationsOut])
async def get_validations(phase: str = None, integration: str = 'Splunk', technique: str = None,
    l1usecase: str = None, l2usecase: str = None):
    ''' Get all Validations that are mapped to ATTCK and have a query available '''
    query = { 'integration': integration, 'technique_name': technique, 
        'kill_chain_phases__startswith': phase, 
        'magma__l1_usecase_name': l1usecase, 'magma__l2_usecase_name': l2usecase 
    }
    validation_objects = Validations.objects(**{k: v for k, v in query.items() if v is not None})
    result = json.loads(validation_objects.to_json())
    return result