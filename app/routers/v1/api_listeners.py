from app.utils import celery
from app.utils.depends import validate_worker, decode_token, validate_token
from fastapi import Depends, Body, APIRouter, Security
from app.schemas.listeners import ListenersOut
from app.schemas.generic import CeleryTask
from typing import List, Dict
from celery import Signature
from celery.result import AsyncResult

router = APIRouter()

# Get active listeners and currently configured options
@router.get('/listeners/{worker_name}', response_model=CeleryTask, dependencies=[Security(validate_token)])
async def get_listeners(worker_name: str, context: dict = Depends(validate_worker), current_user: dict = Depends(decode_token)):
    ''' Get configuration options for all potential listeners by worker name / c2 framework '''
    get_listeners = celery.send_task(context[worker_name]['listeners']['get'], chain=[
        Signature('api.websocket.result.transmit', kwargs={
            'user': current_user['email'],
            'task_type': 'getListeners'
        })
    ])
    return {'task': str(get_listeners)}

@router.get('/state/listeners/get/{job_uuid}', response_model=List[ListenersOut], dependencies=[Security(validate_token)])
async def get_listeners_result(job_uuid: str):
    ''' Get configuration options for all potential listeners by worker name / c2 framework '''
    get_workers = AsyncResult(id=job_uuid, app=celery)
    workers_result = get_workers.get() if get_workers.state == 'SUCCESS' else None
    print(workers_result['response'])
    return workers_result['response']


# Enable a new listener
@router.post('/listeners/{worker_name}/{listener_type}', response_model=CeleryTask, dependencies=[Security(validate_token, scopes=['write:integrations'])])
async def create_listener(worker_name: str, listener_type: str, listener_opts: dict = Body(...),
    context: dict = Depends(validate_worker), current_user: dict = Depends(decode_token)):
    ''' Enable listener for a specific c2 framework '''
    create_listener = celery.send_task(context[worker_name]['listeners']['create'],
            args=(listener_type, listener_opts,), chain=[
                 Signature('api.websocket.result.transmit', kwargs={
                    'user': current_user['email'],
                    'task_type': 'createListener'
                })
            ])
    return {'task': str(create_listener)}

@router.get('/state/listeners/create/{job_uuid}', dependencies=[Security(validate_token)])
async def create_listener_result(job_uuid: str):
    ''' Get configuration options for all potential listeners by worker name / c2 framework '''
    get_workers = AsyncResult(id=job_uuid, app=celery)
    workers_result = get_workers.get() if get_workers.state == 'SUCCESS' else None
    return workers_result['response']


# Disable a running listener
@router.delete('/listener/{worker_name}/{listener_name}', response_model=CeleryTask, dependencies=[Security(validate_token, scopes=['write:integrations'])])
async def delete_listener(worker_name: str, listener_name: str, context: dict = Depends(validate_worker), current_user: dict = Depends(decode_token)):
    ''' Disable enabled listener option by c2 framework and active listener name '''
    delete_listener = celery.send_task(context[worker_name]['listeners']['delete'],
        args=(listener_name,), chain=[
             Signature('api.websocket.result.transmit', kwargs={
                'user': current_user['email'],
                'task_type': 'deleteListener'
            })
        ])
    return {'task': str(delete_listener)}   

@router.get('/state/listener/delete/{job_uuid}', dependencies=[Security(validate_token, scopes=['write:integrations'])])
async def delete_listener_result(job_uuid: str):
    ''' Disable enabled listener option by c2 framework and active listener name '''
    get_workers = AsyncResult(id=job_uuid, app=celery)
    workers_result = get_workers.get() if get_workers.state == 'SUCCESS' else None
    return workers_result['response'] 


# Get options available for all listeners
@router.get('/listeneroptions/{worker_name}', response_model=CeleryTask, dependencies=[Security(validate_token)])
async def get_listener_options(worker_name: str, context: dict = Depends(validate_worker), current_user: dict = Depends(decode_token)):
    ''' Get all available listeners to run by specific c2 framework '''
    get_listeners = celery.send_task(context[worker_name]['listeners']['options'], chain=[
        Signature('api.websocket.result.transmit', kwargs={
            'user': current_user['email'],
            'task_type': 'getListenerOptions'
        })
    ])
    return {'task': str(get_listeners)}

@router.get('/state/listeneroptions/get/{job_uuid}', response_model=Dict[str, Dict], dependencies=[Security(validate_token)])
async def get_listener_options_result(job_uuid: str):
    ''' Get all available listeners to run by specific c2 framework '''
    get_workers = AsyncResult(id=job_uuid, app=celery)
    workers_result = get_workers.get() if get_workers.state == 'SUCCESS' else None
    return workers_result['response'] 
