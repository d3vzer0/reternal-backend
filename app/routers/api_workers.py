from app import celery
from typing import List, Dict
from app.schemas.workers import WorkersOut, WorkersSearchOut
from fastapi import Depends, Body, APIRouter

router = APIRouter()

@router.get('/workers', response_model=Dict[str, WorkersOut])
async def get_workers():
    ''' Get the list of reternal plugins / integrated C2 frameworks '''
    get_workers = celery.send_task('c2.system.workers').get()
    return get_workers

@router.get('/workers/search', response_model=Dict[str, WorkersSearchOut])
async def get_search_workers():
    ''' Get the list of reternal integrated query/search frameworks '''
    get_workers = celery.send_task('search.system.workers').get()
    return get_workers

