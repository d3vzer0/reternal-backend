from fastapi import APIRouter, Security
from celery.result import AsyncResult
from app.utils.depends import validate_token

router = APIRouter()


@router.get('/state/{task_id}', response_model=str, dependencies=[Security(validate_token)])
async def get_task_state(task_id: str):
    task_status = AsyncResult(task_id).state
    return task_status
