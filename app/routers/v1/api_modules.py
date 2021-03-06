from app.utils import celery
from app.utils.depends import validate_worker, validate_token
from fastapi import Depends, APIRouter, Security
from app.schemas.modules import ModuleIn, ModulesOut
from typing import Dict

router = APIRouter() 

@router.get('/modules/{worker_name}', response_model=Dict[str, ModulesOut], dependencies=[Security(validate_token)])
async def get_modules(worker_name: str, context: dict = Depends(validate_worker)):
    ''' Get the available modules/commands by C2 framework / worker '''
    get_modules = celery.send_task(context[worker_name]['modules']['get']).get()['response']
    return get_modules


@router.post('/modules/{worker_name}', dependencies=[Security(validate_token, scopes=['write:integrations'])])
async def run_module(worker_name: str, run_data: ModuleIn, context: dict = Depends(validate_worker)):
    ''' Run a module on an agent specified by the C2 framework name '''
    run_module = celery.send_task(context[worker_name]['modules']['run'], args=(run_data.dict(),)).get()['response']
    return run_module
