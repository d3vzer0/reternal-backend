from fastapi import Depends, APIRouter, Security
from typing import List, Dict
from app.utils.depends import validate_token, decode_token
from app.schemas.sigma import SigmaIn, SigmaOut, SigmaSearchOut, TaskOut
from app.database.models.sigma import Sigma
from app.utils import celery
from app.utils.sigmaloader import Splunk
from celery import Signature
from celery.result import AsyncResult
from starlette.responses import StreamingResponse
import json

QUERYMAPPING = {
    'status': 'status',
    'level': 'level',
    'tags': 'tags',
    'technique': 'techniques.references.0.external_id',
    'technique_name': 'techniques.name',
    'phase': 'techniques.kill_chain_phases',
    'actor': 'techniques.actors.name',
    'data_source': 'techniques.data_sources'
}


router = APIRouter()

async def dynamic_search(search: str = None, level: str = None, phase: str = None, technique_name: str = None,
    l1usecase: str = None, l2usecase: str = None, datasource: str = None, status: str = None,
    technique: str = None, actor: str = None):

    query = {
        'title__contains': search,
        'status': status,
        'level': level,
        'techniques__actors__name': actor,
        'techniques__name': technique_name,
        'techniques__references__external_id': technique,
        'techniques__kill_chain_phases': phase, 
        'techniques__magma__l1_usecase_name__contains': l1usecase, 
        'techniques__magma__l2_usecase_name__contains': l2usecase,
        'techniques__data_sources__contains': datasource
    }
    return {arg: value for arg, value in query.items() if value != None and value != ''}


async def parse_list(fields: str) -> List:
    return fields.split(',')


@router.post('/sigma', response_model=SigmaOut, dependencies=[Security(validate_token, scopes=['write:content'])])
async def create_sigma(sigma: SigmaIn):
    sigma_dict = sigma.dict(exclude_none=True, by_alias=True)
    sigma_dict['sigma_id'] = sigma_dict.pop('id')
    created_sigma_rule = Sigma.objects(hash=sigma_dict['hash']).upsert_one(**sigma_dict)
    return created_sigma_rule.to_dict()


@router.get('/sigma/distinct', response_model=Dict[str, List[str]], dependencies=[Security(validate_token)])
async def get_sigma_distinct(query: dict = Depends(dynamic_search), fields: List[str] = Depends(parse_list)):
    sigma_object = Sigma.objects(**query)
    filtered_fields = [field for field in fields if field in QUERYMAPPING]
    distinct_values = {field: sigma_object.distinct(QUERYMAPPING[field]) for field in filtered_fields}
    return distinct_values


@router.get('/sigma', response_model=SigmaSearchOut, dependencies=[Security(validate_token)])
async def get_sigma_rules(query: dict = Depends(dynamic_search), skip: int = 0, limit: int = 10):
    ''' Get all sigma rules that are mapped to ATTCK and have a query available '''
    sigma_objects = Sigma.objects(**query)
    result = {'total': sigma_objects.count(), 'results': json.loads(sigma_objects[skip:limit].to_json())}
    return result


@router.get('/sigma/package/splunk', response_model=TaskOut, dependencies=[Security(validate_token)])
async def package_sigma_rules_splunk(query: dict = Depends(dynamic_search), current_user: dict = Depends(decode_token)):
    ''' Convert Deux '''
    print('test')
    sigma_rules = json.loads(Sigma.objects(**query).to_json())
    create_package = celery.send_task('api.sigma.package.create',
        args=('splunk', sigma_rules),
        chain=[
            Signature('api.websocket.result.transmit', kwargs={
                'user': current_user['sub'],
                'task_type': 'createSigmaPackage'
            })
        ])
    return {'task': str(create_package)}


@router.get('/sigma/package/splunk/{job_uuid}', dependencies=[Security(validate_token)])
async def get_workers_result(job_uuid: str):
    ''' Get the list of reternal plugins / integrated C2 frameworks '''
    get_workers = AsyncResult(id=job_uuid, app=celery)
    workers_result = get_workers.get() if get_workers.state == 'SUCCESS' else None
    splunk_object = Splunk(workers_result)
    splunk_app = splunk_object.to_archive()
    splunk_app.seek(0)
    
    return StreamingResponse(
        splunk_app,
        media_type='application/gzip',
        headers={
            'Content-Disposition': 'attachment;filename=splunk_sigma_rules.tar.gz'
        }
    )


