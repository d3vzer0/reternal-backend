from app import api, celery
from app.utils.depends import validate_search
from fastapi import Depends, Body
from typing import List, Dict
from celery.result import AsyncResult
import datetime
import json


@api.get('/api/v1/state/{task_id}', response_model=str)
async def get_task_state(task_id: str):
    task_status = AsyncResult(task_id).state
    return task_status
