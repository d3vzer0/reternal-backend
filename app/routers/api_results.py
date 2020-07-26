from fastapi import APIRouter
from app.schemas.results import ResultsIn, ResultsOut, ResultOut
from app.database.models import ExecutedModules
from typing import List
import json

router = APIRouter()

@router.post('/results/module', response_model=List[ResultsOut])
async def update_module_result(result_data: List[ResultsIn]):
    ''' Update results of a module that finished running '''
    update_execution = [ExecutedModules.result(result.dict()) for result in result_data]
    return update_execution 

@router.get('/results', response_model=List[ResultOut])
async def get_task_results(group_id: str):
    ''' Update results of a module that finished running '''
    get_results = json.loads(ExecutedModules.objects(group_id=group_id).to_json())
    return get_results 
