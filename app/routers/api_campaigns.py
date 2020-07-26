from app.utils.scheduler import Scheduler
from app.schemas.campaigns import CampaignsOut, CampaignIn, CreateCampaignOut
from app.schemas.tasks import TasksOut
from app.database.models import Tasks, Campaigns
from fastapi import APIRouter
from typing import List, Dict
import json

router = APIRouter()

@router.post('/campaigns', response_model=List[CreateCampaignOut])
async def create_campaign(campaign: CampaignIn):
    ''' Schedule a new campaign, create individial task document per task '''
    dependent_tasks = [dep.destination for dep in campaign.dependencies]
    create_campaign = Campaigns.create(campaign.dict())
    scheduled_tasks = [ {'campaign': campaign.name, 'group_id': create_campaign['group_id'],
        'scheduled_tasks': await Scheduler(task, {'campaign':campaign.name, 'group_id': create_campaign['group_id']})._organise_tasks() } \
            for task in campaign.tasks if not task.name in dependent_tasks
    ]
    return scheduled_tasks

@router.get('/campaign/{campaign_guid}', response_model=List[TasksOut])
async def get_campaign(campaign_guid):
    ''' Get task status by campaign execution id (guid) '''
    all_tasks = json.loads(Tasks.objects(group_id=campaign_guid).to_json())
    return all_tasks

@router.delete('/campaign/{campaign_guid}', response_model=Dict[str, str])
async def delete_campaign(campaign_guid):
    ''' Delete campaign by campaign execution id (guid) '''
    delete_campaign = Campaigns.delete(campaign_guid)
    return delete_campaign

@router.get('/campaigns', response_model=List[CampaignsOut])
async def get_campaigns():
    ''' Get running tasks grouped by campaigns '''
    all_campaigns = json.loads(Campaigns.objects().to_json())
    return all_campaigns

