from app import api, celery
from app.utils.depends import validate_worker
from fastapi import Depends, Body


@api.get('/api/v1/listeners/{worker_name}')
async def get_listeners(worker_name: str, context: dict = Depends(validate_worker)):
    get_listeners = celery.send_task(context[worker_name]['listeners']['get'],
            retry=True).get()['response']
    return get_listeners

@api.post('/api/v1/listeners/{worker_name}/{listener_type}')
async def create_listener(worker_name: str, listener_type: str, listener_opts: dict = Body(...),
    context: dict = Depends(validate_worker)):
    create_listener = celery.send_task(context[worker_name]['listeners']['create'],
            args=(listener_type, listener_opts,)).get()['response']
    return create_listener

@api.delete('/api/v1/listener/{worker_name}/{listener_name}')
async def delete_listener(worker_name: str, listener_name: str, context: dict = Depends(validate_worker)):
    delete_listener = celery.send_task(context[worker_name]['listeners']['delete'],
        args=(listener_name,)).get()['response']
    return delete_listener   

@api.get('/api/v1/listeners/options/{worker_name}')
async def get_listner_options(worker_name: str, context: dict = Depends(validate_worker)):
    get_listeners = celery.send_task(context[worker_name]['listeners']['options']).get()['response']
    return get_listeners
