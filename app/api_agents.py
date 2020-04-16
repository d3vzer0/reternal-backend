from app import api, celery
from app.utils.depends import validate_worker
from fastapi import Depends, Body


@api.get('/api/v1/agents/{worker_name}')
async def get_agents(worker_name: str, context: dict = Depends(validate_worker)):
    ''' Get registered agents by specified worker / c2 implementation '''
    get_agents = celery.send_task(context[worker_name]['agents']['get'],
        retry=True).get()['response']
    return get_agents
    