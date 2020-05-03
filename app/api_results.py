from app import api, celery
from app.utils.depends import validate_worker
from fastapi import Depends, Body
from app.schemas.results import ResultsIn, ResultsOut
from app.database.models import ExecutedModules
from typing import List

@api.post('/api/v1/results/module', response_model=List[ResultsOut])
async def update_module_result(result_data: List[ResultsIn]):
    ''' Update results of a module that finished running '''
    update_execution = [ExecutedModules.result(result.dict()) for result in result_data]
    return update_execution 
