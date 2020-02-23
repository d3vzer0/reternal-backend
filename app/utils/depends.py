from app import celery
from fastapi import HTTPException

async def validate_worker(worker_name: str):
    get_workers = celery.send_task('c2.system.workers', retry=True).get()
    if worker_name in get_workers and get_workers[worker_name]['enabled']:
        return get_workers
    else:
        raise HTTPException(status_code=400, detail='Worker not configured')
