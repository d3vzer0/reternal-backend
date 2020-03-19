from app import api, celery
from app.utils.depends import validate_worker
from app.schema import CampaignIn, CampaignsOut, CampaignOut, ScheduleOut
from app.schemas import TasksOut
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
    task_content = { 'group_id':group_id, 'task': task['name'], 'campaign': campaign_data['name'],
        'commands': task['commands'], 'sleep': task['sleep'], 'agents': task['agents'],
        'state': 'Open', 'dependencies': [dep['source'] for dep in \
            campaign_data['dependencies'] if dep['destination'] == task['name']] }
    save_task = Tasks.create(task_content)
    return save_task

@api.get('/api/v1/tasks', response_model=List[TasksOut])
async def get_tasks():
    all_tasks = json.loads(Tasks.objects().to_json())
    return all_tasks

@api.post('/api/v1/tasks')
async def create_task(campaign: CampaignIn):
    campaign_data = campaign.dict()
    group_id = uuid.uuid4()
    create_all_tasks = [commit_task(task, campaign_data, group_id) for task in campaign_data['tasks']]
    return create_all_tasks

@api.get('/api/v1/tasks/next', response_model=List[ScheduleOut])
async def get_task_next():
    pipeline = [ {"$unwind": { "path": "$dependencies", "preserveNullAndEmptyArrays": True} },
        { "$lookup": {  "from": "tasks",  "as":"graph",  "let": { "dep": "$dependencies", "old": "$task", "camp": "$campaign"},
        "pipeline": [ { "$match": { "$expr": { "$and": [ { "$eq": [ "$task",  "$$dep" ] },{ "$eq": [ "$state", "Processed" ] },
        { "$eq": [ "$campaign", "$$camp" ] } ] } } } ]  } }, { "$match": { "$or":[{"graph": { "$ne": [] }}, {"dependencies": { "$exists": False }}] } } ]
    result = json.loads(dumps(Tasks.objects(start_date__lte=datetime.now()).aggregate(*pipeline)))
    return result

@api.get('/api/v1/tasks/queue')
async def get_task_queue():
    scheduled_tasks = []
    for worker, tasks in task_inspector.scheduled().items():
        scheduled_tasks = [{'name': task['request']['name'], 'eta':task['eta'],
            'options':task['request']['args'], 'id': task['request']['id']}  for task in tasks]
    return scheduled_tasks
