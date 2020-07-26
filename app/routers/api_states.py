from fastapi import APIRouter
from celery.result import AsyncResult

router = APIRouter()

@router.get('/state/{task_id}', response_model=str)
async def get_task_state(task_id: str):
    task_status = AsyncResult(task_id).state
    return task_status
