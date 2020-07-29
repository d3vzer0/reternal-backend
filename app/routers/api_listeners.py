from app import celery
from app.utils.depends import validate_worker
from fastapi import Depends, Body, APIRouter
from app.schemas.listeners import ListenersOut
from typing import List, Dict

router = APIRouter()

@router.get('/listeners/{worker_name}', response_model=List[ListenersOut])
async def get_listeners(worker_name: str, context: dict = Depends(validate_worker)):
    ''' Get configuration options for all potential listeners by worker name / c2 framework '''
    get_listeners = celery.send_task(context[worker_name]['listeners']['get']).get()['response']
    return get_listeners

@router.post('/listeners/{worker_name}/{listener_type}')
async def create_listener(worker_name: str, listener_type: str, listener_opts: dict = Body(...),
    context: dict = Depends(validate_worker)):
    ''' Enable listener for a specific c2 framework '''
    create_listener = celery.send_task(context[worker_name]['listeners']['create'],
            args=(listener_type, listener_opts,)).get()['response']
    return create_listener

@router.delete('/listener/{worker_name}/{listener_name}')
async def delete_listener(worker_name: str, listener_name: str, context: dict = Depends(validate_worker)):
    ''' Get enabled listener option by c2 framework and active listener name '''
    delete_listener = celery.send_task(context[worker_name]['listeners']['delete'],
        args=(listener_name,)).get()['response']
    return delete_listener   

@router.get('/listeners/options/{worker_name}', response_model=Dict[str, Dict])
async def get_listner_options(worker_name: str, context: dict = Depends(validate_worker)):
    ''' Get all available listeners to run by specific c2 framework '''
    get_listeners = celery.send_task(context[worker_name]['listeners']['options']).get()['response']
    return get_listeners
