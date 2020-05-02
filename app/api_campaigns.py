from app import api, celery
from app.utils.depends import validate_worker
from app.schemas import CampaignsOut, TasksOut
from app.database.models import Tasks
from bson.json_util import dumps
from typing import List
import uuid
import json


@api.get('/api/v1/campaign/{campaign_guid}', response_model=List[TasksOut])
async def get_campaign(campaign_guid):
    ''' Get task status by campaign execution id (guid) '''
    all_tasks = json.loads(Tasks.objects(group_id=campaign_guid).to_json())
    return all_tasks

@api.get('/api/v1/campaigns', response_model=List[CampaignsOut])
async def get_campaigns():
    ''' Get running tasks grouped by campaigns '''
    pipeline = [
        { "$group": { 
            "_id": "$group_id", 
            "campaign": {  "$first": "$campaign" },
            "scheduled_date": { "$first": "$scheduled_date" },
            "tasks": { '$push': "$$ROOT" } 
            } 
        } 
    ]
    campaigns = list(Tasks.objects().aggregate(*pipeline))
    return campaigns