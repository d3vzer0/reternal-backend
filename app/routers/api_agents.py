from app import celery
from app.utils.depends import validate_worker
from fastapi import Depends, APIRouter
from typing import List, Dict

router = APIRouter()

@router.get('/agents/{worker_name}', response_model=List[Dict])
async def get_agents(worker_name: str, context: dict = Depends(validate_worker)):
    ''' Get registered agents by specified worker / c2 implementation '''
    get_agents = celery.send_task(context[worker_name]['agents']['get']).get()['response']
    return get_agents
