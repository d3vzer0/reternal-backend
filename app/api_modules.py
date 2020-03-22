from app import api, celery
from app.utils.depends import validate_worker
from fastapi import Depends, Body


@api.get('/api/v1/modules/{worker_name}')
async def get_modules(worker_name: str, context: dict = Depends(validate_worker)):
    ''' Get the available modules/commands by C2 framework / worker '''
    get_modules = celery.send_task(context[worker_name]['modules']['get']).get()['response']
    return get_modules

