from app import api, celery
from typing import List, Dict
from app.schemas.workers import WorkersOut

@api.get('/api/v1/workers', response_model=Dict[str, WorkersOut])
async def get_workers():
    ''' Get the list of reternal plugins / integrated C2 frameworks '''
    get_workers = celery.send_task('c2.system.workers', retry=True).get()
    return get_workers

