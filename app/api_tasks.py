from app import api, celery
from app.utils.depends import validate_worker
from app.schemas.tasks import TasksOut
from database.models import Tasks
from fastapi import Depends, Body
from typing import List, Dict
import json


@api.get('/api/v1/tasks', response_model=List[TasksOut])
async def get_tasks():
    ''' Get all of the scheduled tasks '''
    all_tasks = json.loads(Tasks.objects().to_json())
    return all_tasks
