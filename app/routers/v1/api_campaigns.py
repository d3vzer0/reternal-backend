from app.utils.scheduler import Scheduler
from app.schemas.campaigns import CampaignsOut, CampaignIn, CreateCampaignOut
from app.schemas.tasks import TasksOut
from app.utils.depends import validate_token
from app.database.models.tasks import Tasks
from app.database.models.campaigns import Campaigns
from fastapi import APIRouter, Depends, Security
from typing import List, Dict
from datetime import datetime
import json


router = APIRouter()


async def dynamic_search(campaign: str = None, agent: str = None, scheduled_date: datetime = None):
    query = {
        'campaign__contains': campaign,
        'nodes__agent__name': agent,
        'nodes__scheduled_date__gte': scheduled_date
    }
    return {arg: value for arg, value in query.items() if value != None and value != ''}


@router.post('/campaigns', response_model=CampaignsOut, dependencies=[Security(validate_token, scopes=['write:content'])])
async def create_campaign(campaign: CampaignIn):
    ''' Schedule a new campaign, create individial task document per task '''
    save_campaign = Campaigns.create(campaign.dict(exclude={'graph'}))
    return save_campaign


@router.get('/campaign/{campaign_guid}', response_model=CampaignsOut, dependencies=[Security(validate_token)])
async def get_campaign(campaign_guid):
    ''' Get task status by campaign execution id (guid) '''
    campaign = json.loads(Campaigns.objects(id=campaign_guid).first().to_json())
    return campaign


@router.delete('/campaign/{campaign_guid}', response_model=Dict[str, str], dependencies=[Security(validate_token, scopes=['write:content'])])
async def delete_campaign(campaign_guid):
    ''' Delete campaign by campaign execution id (guid) '''
    delete_campaign = Campaigns.delete(campaign_guid)
    return delete_campaign


@router.get('/campaigns', response_model=List[CampaignsOut], dependencies=[Security(validate_token)])
async def get_campaigns(query: dict = Depends(dynamic_search)):
    ''' Get running tasks grouped by campaigns '''
    all_campaigns = json.loads(Campaigns.objects(**query).to_json())
    return all_campaigns



