from app import api, celery
from app.utils.depends import validate_worker
from app.schema import CampaignIn, CampaignsOut, CampaignOut
from app.database.models import Campaigns
from fastapi import Depends, Body
from datetime import datetime, timedelta
from celery.task.control import inspect

task_inspector = inspect()
task_schema = ''

@api.get('/api/v1/campaigns', response_model=CampaignsOut)
async def get_campaigns():
    get_campaigns = Campaigns.get()
    return {'campaigns': get_campaigns }


@api.post('/api/v1/campaigns')
async def create_campaign(campaign: CampaignIn):
    save_campaign = Campaigns.create(campaign.dict())
    return save_campaign

@api.get('/api/v1/campaign/{campaign_id}', response_model=CampaignsOut)
async def get_campaign(campaign_id: str):
    get_campaign = Campaigns.get(campaign_id)
    return get_campaign

@api.post('/api/v1/tasks/{worker_name}')
async def create_task(worker_name: str, context: dict = Depends(validate_worker)):
    soon_tm = datetime.now() + timedelta(days=2)
    # schedule_task = celery.send_task(context[worker_name]['tasks']['create'],
    #         retry=True, eta=soon_tm )
    return 'schedule_task'


# @api.post('/api/v1/tasks/{worker_name}')
# async def create_task(worker_name: str, context: dict = Depends(validate_worker)):
#     soon_tm = datetime.now() + timedelta(minutes=2)
#     schedule_task = celery.send_task(context[worker_name]['tasks']['create'],
#             retry=True, eta=soon_tm)
#     return schedule_task


@api.get('/api/v1/tasks/queue')
async def get_task_queue():
    scheduled_tasks = []
    for worker, tasks in task_inspector.scheduled().items():
        scheduled_tasks = [{'name': task['request']['name'], 'eta':task['eta'],
            'options':task['request']['args'], 'id': task['request']['id']}  for task in tasks]
    return scheduled_tasks
