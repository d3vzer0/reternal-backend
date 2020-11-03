from app.utils import celery
from app.utils.depends import validate_worker, decode_token, validate_token
from app.schemas.generic import CeleryTask
from fastapi import Depends, Body, APIRouter, Security
from celery import Signature
from celery.result import AsyncResult

router = APIRouter()

# List available stagers / payloads
@router.get('/stagers/{worker_name}', response_model=CeleryTask, dependencies=[Security(validate_token)])
async def get_stagers(worker_name: str, context: dict = Depends(validate_worker), current_user: dict = Depends(decode_token)):
    ''' Get the list of available stagers with their configuration options by c2 framework / worker '''
    schedule_task = celery.send_task(context[worker_name]['stagers']['get'], chain=[
       Signature('api.websocket.result.transmit', kwargs={
            'user': current_user['email'],
            'task_type': 'getStagers'
        })
    ])
    return {'task': str(schedule_task)}


@router.get('/state/stagers/get/{job_uuid}', dependencies=[Security(validate_token)])
async def get_stagers_result(job_uuid: str):
    ''' Get the list of available stagers with their configuration options by c2 framework / worker '''
    get_workers = AsyncResult(id=job_uuid, app=celery)
    workers_result = get_workers.get() if get_workers.state == 'SUCCESS' else None
    return workers_result['response']


# Generate payload
@router.post('/stagers/{worker_name}', dependencies=[Security(validate_token)])
async def create_stager(worker_name: str, listener_opts: dict = Body(...), context: dict = Depends(validate_worker), current_user: dict = Security(validate_token, scopes=['write:content'])):
    ''' Generate a specific stager '''
    create_stager = celery.send_task(context[worker_name]['stagers']['create'],
        args=(listener_opts,), chain=[
            Signature('api.websocket.result.transmit', kwargs={
                'user': current_user['email'],
                'task_type': 'createStager'
            })
        ])
    return {'task': str(create_stager)}


@router.get('/state/stagers/create/{job_uuid}', dependencies=[Security(validate_token)])
async def create_stager_result(job_uuid: str):
    ''' Generate a specific stager '''
    get_workers = AsyncResult(id=job_uuid, app=celery)
    workers_result = get_workers.get() if get_workers.state == 'SUCCESS' else None
    return workers_result['response']
