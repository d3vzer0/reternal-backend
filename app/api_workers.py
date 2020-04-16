from app import api, celery

@api.get('/api/v1/workers')
async def workers():
    ''' Get the list of reternal plugins / integrated C2 frameworks '''
    get_workers = celery.send_task('c2.system.workers', retry=True).get()
    return get_workers

