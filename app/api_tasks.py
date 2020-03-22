from app import api, celery
from app.utils.depends import validate_worker
from app.schemas import TasksOut, CampaignIn
from app.database.models import Tasks
from fastapi import Depends, Body
from datetime import datetime, timedelta
from celery.task.control import inspect
from bson.json_util import dumps
from typing import List, Dict
import uuid
import json

task_inspector = inspect()
task_schema = ''


def commit_task(task, campaign_data, group_id):
    ''' Commit an individual task in the campaign graph '''
    task_content = { 'group_id':group_id, 'task': task['name'], 'campaign': campaign_data['name'],
        'commands': task['commands'], 'sleep': task['sleep'], 'agents': task['agents'],
        'state': 'Open', 'dependencies': [dep['source'] for dep in \
            campaign_data['dependencies'] if dep['destination'] == task['name']] }
    save_task = Tasks.create(task_content)
    return save_task

@api.get('/api/v1/tasks', response_model=List[TasksOut])
async def get_tasks():
    ''' Get all of the scheduled tasks '''
    all_tasks = json.loads(Tasks.objects().to_json())
    return all_tasks

@api.post('/api/v1/tasks')
async def create_task(campaign: CampaignIn):
    ''' Schedule a new campaign, create individial task document per task '''
    campaign_data = campaign.dict()
    group_id = str(uuid.uuid4())
    create_all_tasks = [commit_task(task, campaign_data, group_id) for task in campaign_data['tasks']]
    return create_all_tasks
