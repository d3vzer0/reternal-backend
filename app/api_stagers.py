from app import api, celery
from app.utils.depends import validate_worker
from fastapi import Depends, Body


@api.get('/api/v1/stagers/{worker_name}')
async def get_stagers(worker_name: str, context: dict = Depends(validate_worker)):
    ''' Get the list of available stagers with their configuration options by c2 framework / worker '''
    get_stagers = celery.send_task(context[worker_name]['stagers']['get'],
        retry=True).get()['response']
    return get_stagers

@api.post('/api/v1/stagers/{worker_name}')
async def create_stager(worker_name: str, listener_opts: dict = Body(...), context: dict = Depends(validate_worker)):
    ''' Generate a specific stager '''
    create_stager = celery.send_task(context[worker_name]['stagers']['create'],
        args=(listener_opts,), retry=True).get()['response']
    return create_stager
