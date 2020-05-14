from app import api, celery
from app.utils.depends import validate_search
from fastapi import Depends, Body
from app.schemas.searchcoverage import TaskOut
from workers.search.tasks import update_logsources
from typing import List, Dict
import datetime

@api.get('/api/v1/search/{worker_name}/sourcetypes', response_model=TaskOut)
async def get_listeners(worker_name: str, earliest_time: str = '-900d', latest_time: str = 'now', context: dict = Depends(validate_search)):
    ''' Get logsources available from specified worker '''
    get_logsources = celery.send_task(context[worker_name]['query']['sourcetypes'],
            args=(earliest_time, latest_time), link=update_logsources.s(worker_name, datetime.datetime.now()))
    return {'task': str(get_logsources)}

