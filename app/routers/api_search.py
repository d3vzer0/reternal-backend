from app import celery
from app.database.models import SourceTypes
from app.utils.depends import validate_search
from fastapi import Depends, APIRouter
from app.schemas.searchcoverage import TaskOut, SourcetypesOut
from app.workers.search.tasks import update_logsources, update_indices
from typing import List
import datetime
import json

router = APIRouter()

@router.post('/search/{worker_name}/sourcetypes', response_model=TaskOut)
async def query_sourcetypes(worker_name: str, earliest_time: str = '-900d', latest_time: str = 'now', context: dict = Depends(validate_search)):
    ''' Get sourcetype event counts from specified worker '''
    get_logsources = celery.send_task(context[worker_name]['sourcetypes']['run'],
            args=(earliest_time, latest_time), link=update_logsources.s(worker_name, datetime.datetime.now()))
    return {'task': str(get_logsources)}


@router.post('/search/{worker_name}/indices', response_model=TaskOut)
async def query_indices(worker_name: str, earliest_time: str = '-900d', latest_time: str = 'now', context: dict = Depends(validate_search)):
    ''' Get sourcetype by index and source from specified worker '''
    get_logsources = celery.send_task(context[worker_name]['indices']['run'],
            args=(earliest_time, latest_time), link=update_indices.s(worker_name, datetime.datetime.now()))
    return {'task': str(get_logsources)}

@router.get('/search/{worker_name}/sourcetypes', response_model=List[SourcetypesOut])
async def get_validations():
    ''' Get all sourcetypes known by Splunk '''
    all_sourcetypes = SourceTypes.objects()
    result = json.loads(all_sourcetypes.to_json())
    return result
