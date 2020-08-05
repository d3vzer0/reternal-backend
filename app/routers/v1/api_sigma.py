from app.database.models import Sigma
from fastapi import Depends, APIRouter
from app.schemas.sigma import SigmaIn, SigmaOut, SigmaRules
from typing import List
from app.utils.sigmaloader import SigmaLoader
import json

router = APIRouter()

async def dynamic_search(search: str = None, level: str = None, phase: str = None, technique: str = None,
    l1usecase: str = None, l2usecase: str = None, datasource: str = None, status: str = None,
    technique_id: str = None ):

    query = {
        'title__contains': search,
        'status': status,
        'level': level,
        'techniques__name': technique,
        'techniques__references__external_id': technique_id,
        'techniques__kill_chain_phases': phase, 
        'techniques__magma__l1_usecase_name__contains': l1usecase, 
        'techniques__magma__l2_usecase_name__contains': l2usecase,
        'techniques__data_sources__contains': datasource
    }
    return {arg: value for arg, value in query.items() if value is not None and value is not ''}

@router.post('/sigma', response_model=SigmaOut)
async def create_sigma(sigma: SigmaIn):
    create_rule = Sigma.create(**sigma.dict(exclude_none=True))
    return create_rule

@router.get('/sigma/techniqueids')
async def get_sigma_techniques_by_id(query: dict = Depends(dynamic_search)):
    ''' Get all unique techniques by ID for available sigma rules '''
    unique_techniques = Sigma.objects(**query).distinct('techniques.references.0.external_id')
    return unique_techniques

@router.get('/sigma/phases')
async def get_sigma_phases(query: dict = Depends(dynamic_search)):
    ''' Get all unique phases for available sigma rules '''
    unique_phases = Sigma.objects(**query).distinct('techniques.kill_chain_phases')
    return unique_phases

@router.get('/sigma/tags')
async def get_sigma_tags(query: dict = Depends(dynamic_search)):
    ''' Get all unique tags for available sigma rules '''
    # print(query)
    unique_phases = Sigma.objects(**query).distinct('tags')
    return unique_phases

@router.get('/sigma/status')
async def get_sigma_status(query: dict = Depends(dynamic_search)):
    ''' Get all unique status for available sigma rules '''
    print(query)
    unique_status = Sigma.objects(**query).distinct('status')
    return unique_status

@router.get('/sigma/level')
async def get_sigma_level(query: dict = Depends(dynamic_search)):
    ''' Get all unique level for available sigma rules '''
    unique_level = Sigma.objects(**query).distinct('level')
    return unique_level

@router.get('/sigma/datasources')
async def get_sigma_datasources(query: dict = Depends(dynamic_search)):
    ''' Get all unique datasources for available sigma rules '''
    unique_datasources = Sigma.objects(**query).distinct('techniques.data_sources')
    return unique_datasources

@router.get('/sigma/techniques', response_model=List[str])
async def get_validation_techniques(query: dict = Depends(dynamic_search)):
    ''' Get all unique phases for available sigma rules '''
    unique_phases = Sigma.objects(**query).distinct('techniques.technique_name')
    return unique_phases

@router.get('/sigma/l1usecases', response_model=List[str])
async def get_l1_usecases(query: dict = Depends(dynamic_search)):
    ''' Get all unique L1 usecases for available sigma rules '''
    unique_usecases = Sigma.objects(**query).distinct('techniques.magma.l1_usecase_name')
    return unique_usecases

@router.get('/sigma/l2usecases', response_model=List[str])
async def get_l2_usecases(query: dict = Depends(dynamic_search)):
    ''' Get all unique L2 usecases for available sigma rules '''
    unique_usecases = Sigma.objects(**query).distinct('techniques.magma.l2_usecase_name')
    return unique_usecases

@router.get('/sigma', response_model=List[SigmaOut])
async def get_sigma_rules(query: dict = Depends(dynamic_search)):
    ''' Get all sigma rules that are mapped to ATTCK and have a query available '''
    sigma_objects = Sigma.objects.filter(**query)
    result = json.loads(sigma_objects.to_json())
    return result

@router.get('/sigma/convert/{target}')
async def convert_sigma_rules(query: dict = Depends(dynamic_search), target: str = 'splunk') :
    ''' Convert selection of sigma rules to specified target platform '''
    sigma_rules = json.loads(Sigma.objects(**query).to_json())
    format_rules = SigmaRules(**{'each_rule': sigma_rules}).dict(by_alias=True, exclude_none=True)
    target_rules = SigmaLoader().convert_rules(format_rules['each_rule'])
    return target_rules
