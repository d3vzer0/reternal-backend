from database.models import Sigma
from app import api, celery
from app.utils.depends import validate_worker
from fastapi import Depends, Body
from app.schemas.validations import SigmaIn, SigmaOut
from bson.json_util import dumps
from typing import List, Dict
import json


async def dynamic_search(phase: str = None, technique: str = None,
    l1usecase: str = None, l2usecase: str = None, datasource: str = None):
    query = { 
        'techniques__name': technique, 
        'techniques__kill_chain_phases': phase, 
        'techniques__magma__l1_usecase_name': l1usecase, 
        'techniques__magma__l2_usecase_name': l2usecase,
        'techniques__data_sources__contains': datasource
    }
    return {arg: value for arg, value in query.items() if value is not None}

@api.post('/api/v1/sigma', response_model=SigmaOut)
async def create_sigma(sigma: SigmaIn):
    create_rule = Sigma.create(**sigma.dict(exclude_none=True))
    return create_rule

@api.post('/api/v1/sigma/phases')
async def get_sigma_phases(query: dict = Depends(dynamic_search)):
    ''' Get all unique phases for available sigma rules '''
    unique_phases = Sigma.objects(**query).distinct('techniques.kill_chain_phases')
    return unique_phases

@api.get('/api/v1/sigma/datasources')
async def get_sigma_datasources(query: dict = Depends(dynamic_search)):
    ''' Get all unique datasources for available sigma rules '''
    unique_datasources = Sigma.objects(**query).distinct('techniques.data_sources')
    return unique_datasources

@api.get('/api/v1/sigma/techniques', response_model=List[str])
async def get_validation_techniques(query: dict = Depends(dynamic_search)):
    ''' Get all unique phases for available sigma rules '''
    unique_phases = Sigma.objects(**query).distinct('techniques.technique_name')
    return unique_phases

@api.get('/api/v1/sigma/l1usecases', response_model=List[str])
async def get_l1_usecases(query: dict = Depends(dynamic_search)):
    ''' Get all unique L1 usecases for available sigma rules '''
    unique_usecases = Sigma.objects(**query).distinct('techniques.magma.l1_usecase_name')
    return unique_usecases

@api.get('/api/v1/sigma/l2usecases', response_model=List[str])
async def get_l2_usecases(query: dict = Depends(dynamic_search)):
    ''' Get all unique L2 usecases for available sigma rules '''
    unique_usecases = Sigma.objects(**query).distinct('techniques.magma.l2_usecase_name')
    return unique_usecases

@api.get('/api/v1/sigma', response_model=List[SigmaOut])
async def get_validations(query: dict = Depends(dynamic_search)):
    ''' Get all sigma rules that are mapped to ATTCK and have a query available '''
    sigma_objects = Sigma.objects(**query)
    result = json.loads(sigma_objects.to_json())
    return result


# @api.post('/api/v1/validations', response_model=ValidationsOut)
# async def create_validations(validation: ValidationsIn):
#     create_validation = Validations.create(**validation.dict())
#     return create_validation

# @api.get('/api/v1/validations/integrations', response_model=List[str])
# async def get_validation_integrations():
#     ''' Get all unique integrations for available queries '''
#     unique_integrations = Validations.objects().distinct('integration')
#     return unique_integrations

# @api.get('/api/v1/validations/phases', response_model=List[str])
# async def get_validation_phases(query: dict = Depends(dynamic_search)):
#     ''' Get all unique phases for available queries '''
#     unique_phases = Validations.objects(**query).distinct('kill_chain_phases')
#     return unique_phases

# @api.get('/api/v1/validations/datasources')
# async def get_validation_datasources(query: dict = Depends(dynamic_search)):
#     ''' Get all unique datasources for available queries '''
#     unique_datasources = Validations.objects(**query).distinct('data_sources')
#     return unique_datasources

# @api.get('/api/v1/validations/techniques', response_model=List[str])
# async def get_validation_techniques(query: dict = Depends(dynamic_search)):
#     ''' Get all unique phases for available queries '''
#     unique_phases = Validations.objects(**query).distinct('technique_name')
#     return unique_phases

# @api.get('/api/v1/validations/l1usecases', response_model=List[str])
# async def get_l1_usecases(query: dict = Depends(dynamic_search)):
#     ''' Get all unique L1 usecases for available queries '''
#     unique_usecases = Validations.objects(**query).distinct('magma.l1_usecase_name')
#     return unique_usecases

# @api.get('/api/v1/validations/l2usecases', response_model=List[str])
# async def get_l2_usecases(query: dict = Depends(dynamic_search)):
#     ''' Get all unique L2 usecases for available queries '''
#     unique_usecases = Validations.objects(**query).distinct('magma.l2_usecase_name')
#     return unique_usecases

# @api.get('/api/v1/validations', response_model=List[ValidationsOut])
# async def get_validations(query: dict = Depends(dynamic_search)):
#     ''' Get all Validations that are mapped to ATTCK and have a query available '''
#     validation_objects = Validations.objects(**query)
#     result = json.loads(validation_objects.to_json())
#     return result
