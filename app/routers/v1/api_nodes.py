from app.utils import celery
from app.utils.depends import job_uuid, decode_token, validate_token
from app.schemas.nodes import Node
from typing import List, Dict, Any

from app.schemas.generic import CeleryTask
from fastapi import APIRouter, Depends, Security
from celery.result import AsyncResult
from celery import Signature
from typing import Dict

router = APIRouter()


@router.get('/nodes', response_model=CeleryTask, dependencies=[Security(validate_token)])
async def get_nodes(current_user: dict = Depends(decode_token)):
    ''' Get the list of reternal plugins / integrated nodes '''
    schedule_task = celery.send_task('nodes.system.get', chain=[
        Signature('api.websocket.result.transmit', kwargs={
            'user': current_user['sub'],
            'task_type': 'getNodes'
        })
    ])
    return {'task': str(schedule_task) }


@router.get('/state/nodes/get/{job_uuid}', response_model=List[Node], response_model_exclude_unset=True, dependencies=[Security(validate_token)])
async def get_nodes_result(job_uuid: str):
    ''' Get the list of reternal plugins / integrated C2 frameworks '''
    get_nodes = AsyncResult(id=job_uuid, app=celery)
    nodes_result = get_nodes.get() if get_nodes.state == 'SUCCESS' else None
    return nodes_result

