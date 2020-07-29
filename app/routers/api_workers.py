from app.utils import celery
from app.utils.depends import job_uuid, validate_token
from app.schemas.workers import WorkersOut, WorkersSearchOut
from app.schemas.generic import CeleryTask
from app.workers.websocket.tasks.results import transmit_result
from fastapi import APIRouter, Depends
from celery.result import AsyncResult
from typing import Dict

router = APIRouter()

# @router.get('/workers', response_model=Dict[str, str])
# async def get_workers():
#     ''' Get the list of reternal plugins / integrated C2 frameworks '''
#     get_workers = celery.send_task('c2.system.workers', 
#         link=transmit_result.s('jdreijer@d3vzer0.com'))
#     return {'task': str(get_workers)}

@router.get('/workers/c2', response_model=CeleryTask)
async def get_workers(current_user: dict = Depends(validate_token), job_uuid: str = Depends(job_uuid)):
    ''' Get the list of reternal plugins / integrated C2 frameworks '''
    celery.send_task('c2.system.workers', task_id=job_uuid, link=transmit_result.s(job_uuid, current_user['email']))
    return {'task': job_uuid }

@router.get('/workers/c2/{job_uuid}', response_model=Dict[str, WorkersOut])
async def get_workers_result(job_uuid: str, current_user: dict = Depends(validate_token)):
    ''' Get the list of reternal plugins / integrated C2 frameworks '''
    get_workers = AsyncResult(job_uuid, app=celery).get()
    return get_workers

@router.get('/workers/search', response_model=CeleryTask)
async def get_search_workers(current_user: dict = Depends(validate_token), job_uuid: str = Depends(job_uuid)):
    ''' Get the list of reternal integrated query/search frameworks '''
    celery.send_task('search.system.workers', task_id=job_uuid, link=transmit_result.s(job_uuid, current_user['email']))
    return {'task': job_uuid }

@router.get('/workers/search/{job_uuid}', response_model=Dict[str, WorkersSearchOut])
async def get_search_workers_result(job_uuid: str, current_user: dict = Depends(validate_token)):
    ''' Get the list of reternal integrated query/search frameworks '''
    get_workers = AsyncResult(job_uuid, app=celery).get()
    return get_workers


