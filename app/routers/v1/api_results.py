from fastapi import APIRouter, Security
from app.utils.depends import validate_token
from app.schemas.results import ResultsIn, ResultsOut, ResultOut
from app.database.models.executedmodules import ExecutedModules
from typing import List
import json

router = APIRouter()


@router.post('/results/module', response_model=List[ResultsOut], dependencies=[Security(validate_token, scopes=['write:scheduling'])])
async def update_module_result(result_data: List[ResultsIn]):
    ''' Update results of a module that finished running '''
    update_execution = [ExecutedModules.result(result.dict()) for result in result_data]
    return update_execution 


@router.get('/results', response_model=List[ResultOut], dependencies=[Security(validate_token)])
async def get_task_results(group_id: str):
    ''' Update results of a module that finished running '''
    get_results = json.loads(ExecutedModules.objects(group_id=group_id).to_json())
    return get_results 
