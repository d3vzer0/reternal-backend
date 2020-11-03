from bson import decode
from app.utils import celery
from app.utils.depends import validate_worker, decode_token, validate_token
from app.schemas.generic import CeleryTask
from fastapi import Depends, APIRouter, Security
from typing import List, Dict
from celery import Signature
from celery.result import AsyncResult


router = APIRouter()

# Get list of active agents
@router.get('/agents/{worker_name}', response_model=CeleryTask, dependencies=[Security(validate_token)])
async def get_agents(worker_name: str, context: dict = Depends(validate_worker), current_user: dict = Depends(decode_token)):
    ''' Get registered agents by specified worker / c2 implementation '''
    get_agents = celery.send_task(context[worker_name]['agents']['get'], chain=[
        Signature('api.websocket.result.transmit', kwargs={
            'user': current_user['email'],
            'task_type': 'getAgents'
        })
    ])
    return {'task': str(get_agents)}

@router.get('/state/agents/get/{job_uuid}', response_model=List[Dict], dependencies=[Security(validate_token)])
async def get_agents_result(job_uuid: str):
    ''' Get registered agents by specified worker / c2 implementation '''
    get_workers = AsyncResult(id=job_uuid, app=celery)
    workers_result = get_workers.get() if get_workers.state == 'SUCCESS' else None
    return workers_result['response']


# Stop active agent
@router.get('/agents/{worker_name}/{agent_id}/stop', response_model=CeleryTask, dependencies=[Security(validate_token, scopes=['write:integrations'])])
async def stop_agent(worker_name: str, agent_id: str, context: dict = Depends(validate_worker), current_user: dict = Depends(decode_token)):
    ''' Kill/stop active agent (does not remove state from backend)'''
    stop_agent = celery.send_task(context[worker_name]['agents']['stop'], 
        args=(agent_id,), chain=[
            Signature('api.websocket.result.transmit', kwargs={
                'user': current_user['email'],
                'task_type': 'stopAgent'
            })
        ])
    return {'task': str(stop_agent)}

@router.get('/state/agents/stop/{job_uuid}', response_model=List[Dict], dependencies=[Security(validate_token, scopes=['write:integrations'])])
async def stop_agent_result(job_uuid: str):
    ''' Kill/stop active agent (does not remove state from backend)'''
    get_workers = AsyncResult(id=job_uuid, app=celery)
    workers_result = get_workers.get() if get_workers.state == 'SUCCESS' else None
    return workers_result['response']


# Delete active or passive agent
@router.delete('/agents/{worker_name}/{agent_id}', response_model=CeleryTask, dependencies=[Security(validate_token, scopes=['write:integrations'])])
async def delete_agent(worker_name: str, agent_id: str, context: dict = Depends(validate_worker), current_user: dict = Depends(decode_token)):
    ''' Deletes agent from backend '''
    delete_agent = celery.send_task(context[worker_name]['agents']['delete'],
        args=(agent_id,), chain=[
            Signature('api.websocket.result.transmit', kwargs={
                'user': current_user['email'],
                'task_type': 'deleteAgent'
            })
        ])
    return {'task': str(delete_agent)}

@router.get('/state/agents/stop/{job_uuid}', response_model=List[Dict], dependencies=[Security(validate_token)])
async def delete_agent_result(job_uuid: str):
    ''' Deletes agent from backend '''
    get_workers = AsyncResult(id=job_uuid, app=celery)
    workers_result = get_workers.get() if get_workers.state == 'SUCCESS' else None
    return workers_result['response']

