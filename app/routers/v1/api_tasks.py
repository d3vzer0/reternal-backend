from app.schemas.tasks import TasksOut
from app.database.models.tasks import Tasks
from app.utils.depends import validate_token
from fastapi import APIRouter, Security
from typing import List
import json

router = APIRouter()

@router.get('/tasks', response_model=List[TasksOut], dependencies=[Security(validate_token)])
async def get_tasks():
    ''' Get all of the scheduled tasks '''
    all_tasks = json.loads(Tasks.objects().to_json())
    return all_tasks
