from app.database.models.products import SourceTypes
from app.utils.depends import validate_search, decode_token
from fastapi import Depends, APIRouter
from app.schemas.searchcoverage import TaskOut, SourcetypesOut
from app.utils import celery
from celery import Signature
from typing import List
import datetime
import json

router = APIRouter()


@router.post('/search/{worker_name}/sourcetypes', response_model=TaskOut)
async def query_sourcetypes(worker_name: str, earliest_time: str = '-900d', latest_time: str = 'now', context: dict = Depends(validate_search), current_user: dict = Depends(decode_token)):
    ''' Get sourcetype event counts from specified worker '''
    get_logsources = celery.send_task(context[worker_name]['sourcetypes']['run'],
            args=(earliest_time, latest_time), 
            chain=[
                Signature('api.logsources.task.update', args=(worker_name, datetime.datetime.now())),
                Signature('api.websocket.result.transmit', kwargs={
                    'user': current_user['sub'],
                    'task_type': 'getListeners'
                })
            ])
    return {'task': str(get_logsources)}


@router.post('/search/{worker_name}/indices', response_model=TaskOut)
async def query_indices(worker_name: str, earliest_time: str = '-900d', latest_time: str = 'now', context: dict = Depends(validate_search), current_user: dict = Depends(decode_token)):
    ''' Get sourcetype by index and source from specified worker '''
    get_logsources = celery.send_task(context[worker_name]['indices']['run'],
            args=(earliest_time, latest_time),
            chain=[
                Signature('api.indices.task.update', args=(worker_name, datetime.datetime.now())),
                Signature('api.websocket.result.transmit', kwargs={
                    'user': current_user['sub'],
                    'task_type': 'getListeners'
                })
            ])
    return {'task': str(get_logsources)}

@router.get('/search/{worker_name}/sourcetypes', response_model=List[SourcetypesOut])
async def get_validations():
    ''' Get all sourcetypes known by Splunk '''
    all_sourcetypes = SourceTypes.objects()
    result = json.loads(all_sourcetypes.to_json())
    return result
