from app import api, celery
from typing import List, Dict
from app.schemas.workers import WorkersOut, WorkersSearchOut

@api.get('/api/v1/workers', response_model=Dict[str, WorkersOut])
async def get_workers():
    ''' Get the list of reternal plugins / integrated C2 frameworks '''
    get_workers = celery.send_task('c2.system.workers').get()
    return get_workers

@api.get('/api/v1/workers/search', response_model=Dict[str, WorkersSearchOut])
async def get_search_workers():
    ''' Get the list of reternal integrated query/search frameworks '''
    get_workers = celery.send_task('search.system.workers').get()
    return get_workers

