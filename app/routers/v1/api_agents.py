from app.utils import celery
from app.utils.depends import validate_worker, decode_token
from app.schemas.generic import CeleryTask
from fastapi import Depends, APIRouter
from typing import List, Dict
from celery import Signature
from celery.result import AsyncResult


router = APIRouter()

# Get list of active agents
@router.get('/agents/{worker_name}', response_model=CeleryTask)
async def get_agents(worker_name: str, context: dict = Depends(validate_worker), current_user: dict = Depends(decode_token)):
    ''' Get registered agents by specified worker / c2 implementation '''
    get_agents = celery.send_task(context[worker_name]['agents']['get'], chain=[
        Signature('api.websocket.result.transmit', kwargs={
            'user': current_user['email'],
            'task_type': 'getAgents'
        })
    ])
    return {'task': str(get_agents)}

@router.get('/state/agents/get/{job_uuid}', response_model=List[Dict])
async def get_agents_result(job_uuid: str):
    ''' Get registered agents by specified worker / c2 implementation '''
    get_workers = AsyncResult(id=job_uuid, app=celery)
    workers_result = get_workers.get() if get_workers.state == 'SUCCESS' else None
    return workers_result['response']

