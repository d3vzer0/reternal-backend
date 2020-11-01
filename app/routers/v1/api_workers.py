from app.utils import celery
from app.utils.depends import job_uuid, decode_token
from app.schemas.workers import WorkersOut, WorkersSearchOut
from app.schemas.generic import CeleryTask
from fastapi import APIRouter, Depends
from celery.result import AsyncResult
from celery import Signature
from typing import Dict

router = APIRouter()


@router.get('/workers/c2', response_model=CeleryTask)
async def get_workers(current_user: dict = Depends(decode_token)):
    ''' Get the list of reternal plugins / integrated C2 frameworks '''
    schedule_task = celery.send_task('c2.system.workers', chain=[
        Signature('api.websocket.result.transmit', kwargs={
            'user': current_user['sub'],
            'task_type': 'getWorkersC2'
        })
    ])
    return {'task': str(schedule_task) }


@router.get('/workers/c2/{job_uuid}', response_model=Dict[str, WorkersOut])
async def get_workers_result(job_uuid: str):
    ''' Get the list of reternal plugins / integrated C2 frameworks '''
    get_workers = AsyncResult(id=job_uuid, app=celery)
    workers_result = get_workers.get() if get_workers.state == 'SUCCESS' else None
    return workers_result


@router.get('/workers/search', response_model=CeleryTask)
async def get_workers_search(current_user: dict = Depends(decode_token)):
    ''' Get the list of reternal plugins / integrated C2 frameworks '''
    schedule_task = celery.send_task('search.system.workers', chain=[
        Signature('api.websocket.result.transmit', kwargs={
            'user': current_user['sub'],
            'task_type': 'getWorkersSearch'
        })
    ])
    return {'task': str(schedule_task) }


@router.get('/workers/search/{job_uuid}', response_model=Dict[str, WorkersSearchOut])
async def get_search_workers_result(job_uuid: str):
    ''' Get the list of reternal integrated query/search frameworks '''
    get_workers = AsyncResult(id=job_uuid, app=celery)
    workers_result = get_workers.get() if get_workers.state == 'SUCCESS' else None
    return workers_result