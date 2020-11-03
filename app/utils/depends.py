from codecs import decode
from app.utils import celery
from app.environment import config
from app.utils.jwtdecode import JWT
from fastapi import HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
import hashlib

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='token',
    scopes={
        'write:content': 'Write permissions to modify core content',
        'write:scheduling': 'Write permissions to schedule tasks',
        'write:integrations': 'Write permissions to run integrations'
    },
)

async def validate_worker(worker_name: str):
    get_workers = celery.send_task('c2.system.workers', task_id='get_active_workers').get()
    if worker_name in get_workers and get_workers[worker_name]['enabled']:
        return get_workers
    else:
        raise HTTPException(status_code=400, detail='Worker not configured or worker is disabled')

async def validate_search(worker_name: str):
    get_workers = celery.send_task('search.system.workers').get()
    if worker_name in get_workers and get_workers[worker_name]['enabled']:
        return get_workers
    else:
        raise HTTPException(status_code=400, detail='Worker not configured or worker is disabled')

async def decode_token(token: str = Depends(oauth2_scheme)):
    decode_token = JWT(config['OAUTH2_OPENID_CONFIG'], config['OAUTH2_ISSUER'],
        config['OAUTH2_AUDIENCE']).decode(token, verify=False)
    return decode_token

async def validate_token(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)):
    # for scope in security_scopes.scopes:
        # print(scope)
        # if scope not in token_data.scopes:
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="Not enough permissions",
        #         headers={"WWW-Authenticate": authenticate_value},
    decode_token = JWT(config['OAUTH2_OPENID_CONFIG'], config['OAUTH2_ISSUER'],
        config['OAUTH2_AUDIENCE']).decode(token, verify=True)
    return decode_token

async def job_uuid(request: Request):
    job_uuid = hashlib.sha224(request.url.path.encode('utf-8')).hexdigest()
    return job_uuid
