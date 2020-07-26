from app import celery
from app.environment import config
from app.utils.jwt_validation import JWT
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def validate_worker(worker_name: str):
    get_workers = celery.send_task('c2.system.workers').get()
    if worker_name in get_workers and get_workers[worker_name]['enabled']:
        return get_workers
    else:
        raise HTTPException(status_code=400, detail='Worker not configured')

async def validate_search(worker_name: str):
    get_workers = celery.send_task('search.system.workers').get()
    if worker_name in get_workers and get_workers[worker_name]['enabled']:
        return get_workers
    else:
        raise HTTPException(status_code=400, detail='Worker not configured')

async def validate_token(token: str = Depends(oauth2_scheme)):
    decode_token = JWT(config['OAUTH2_OPENID_CONFIG'], config['OAUTH2_ISSUER'],
        config['OAUTH2_AUDIENCE']).validate(token)
    return decode_token
