from app import api, celery
from app.utils.depends import validate_worker
from app.schemas.campaigns import CampaignsOut, CampaignIn, CampaignDenomIn, CreateCampaignOut
from app.schemas.tasks import TasksOut
from app.database.models import Tasks, Campaigns, ExecutedModules
from workers.scheduler import update_task
from bson.json_util import dumps
from typing import List, Dict
from datetime import datetime, timedelta
import pytz
import json


class Scheduler:
    def __init__(self, task):
        self.task = task

    async def _queue_task(self, agent):
        available_workers = await validate_worker(agent.integration)
        execution_process = available_workers[agent.integration]['modules']['run']
        planned_tasks = [
            str(celery.send_task(execution_process, args=({'module':module.module, 'input': module.input, 'agent':agent.id},),
                eta=self.task.scheduled_date.astimezone(pytz.utc), link=update_task.s())) for module in self.task.commands ]
        return planned_tasks

    async def _organise_tasks(self):
        planned_modules = [{'agent': agent.name, 'queue': await self._queue_task(agent)} for agent in self.task.agents]
        return planned_modules


@api.post('/api/v1/campaigns', response_model=List[CreateCampaignOut])
async def create_campaign(campaign: CampaignIn):
    ''' Schedule a new campaign, create individial task document per task '''
    dependent_tasks = [dep.destination for dep in campaign.dependencies]
    create_campaign = Campaigns.create(campaign.dict())
    scheduled_tasks = [
        {'campaign': campaign.name, 'group_id': create_campaign['group_id'],
        'scheduled_tasks': await Scheduler(task)._organise_tasks() } \
            for task in campaign.tasks  if not task.name in dependent_tasks]
    return scheduled_tasks

@api.get('/api/v1/campaign/{campaign_guid}', response_model=List[TasksOut])
async def get_campaign(campaign_guid):
    ''' Get task status by campaign execution id (guid) '''
    all_tasks = json.loads(Tasks.objects(group_id=campaign_guid).to_json())
    return all_tasks

@api.delete('/api/v1/campaign/{campaign_guid}', response_model=Dict[str, str])
async def delete_campaign(campaign_guid):
    ''' Delete campaign by campaign execution id (guid) '''
    delete_campaign = Campaigns.delete(campaign_guid)
    return delete_campaign

@api.get('/api/v1/campaigns', response_model=List[CampaignsOut])
async def get_campaigns():
    ''' Get running tasks grouped by campaigns '''
    all_campaigns = json.loads(Campaigns.objects().to_json())
    return all_campaigns