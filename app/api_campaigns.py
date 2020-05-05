from app import api, celery
from app.utils.depends import validate_worker
from app.schemas.campaigns import CampaignsOut, CampaignIn, CampaignDenomIn, CreateCampaignOut
from app.schemas.tasks import TasksOut
from app.database.models import Tasks, Campaigns
from bson.json_util import dumps
from typing import List, Dict
import json

@api.post('/api/v1/campaigns', response_model=CreateCampaignOut)
async def create_campaign(campaign: CampaignIn):
    ''' Schedule a new campaign, create individial task document per task '''
    create_campaign = Campaigns.create(campaign.dict())
    return create_campaign

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