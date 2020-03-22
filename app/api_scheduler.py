from app import api, celery
from app.utils.depends import validate_worker
from app.schemas import PlanTaskIn, ScheduleOut
from app.database.models import Tasks, ExecutedModules
from fastapi import Depends, Body
from datetime import datetime, timedelta
from celery.task.control import inspect
from bson.json_util import dumps
from typing import List, Dict
from app.api_modules import run_module
import uuid
import json

task_inspector = inspect()
task_schema = ''


@api.get('/api/v1/scheduler/next', response_model=List[ScheduleOut])
async def get_task_next() -> list:
    ''' Calculate the next task to be executed, following the graph dependencies '''
    pipeline = [ {"$unwind": { "path": "$dependencies", "preserveNullAndEmptyArrays": True} },
        { "$lookup": {  "from": "tasks",  "as":"graph",  "let": { "dep": "$dependencies", "old": "$task", "camp": "$campaign"},
        "pipeline": [ { "$match": { "$expr": { "$and": [ { "$eq": [ "$task",  "$$dep" ] },{ "$eq": [ "$state", "Processed" ] },
        { "$eq": [ "$campaign", "$$camp" ] } ] } } } ]  } }, { "$match": { "$or":[{"graph": { "$ne": [] }}, {"dependencies": { "$exists": False }}] } } ]
    result = json.loads(dumps(Tasks.objects(start_date__lte=datetime.now()).aggregate(*pipeline)))
    return result

@api.get('/api/v1/scheduler/queue')
async def get_task_queue():
    ''' Get the list of tasks that are currently executing '''
    scheduled_tasks = []
    for worker, tasks in task_inspector.scheduled().items():
        scheduled_tasks = [{'name': task['request']['name'], 'eta':task['eta'],
            'options':task['request']['args'], 'id': task['request']['id']} for task in tasks]
    return scheduled_tasks

async def call_integration(module, module_input, agent_id, integration) -> dict:
    ''' Call the C2 API and run command. Return the external execution ID '''
    available_workers = await validate_worker(integration)
    execution_process = available_workers[integration]['modules']['run']
    execute_worker = celery.send_task(execution_process, args=({'module':module, 'input': module_input,
        'agent':agent_id},)).get()['response']
    return {'module':module, 'external_id': execute_worker['external_id']}

async def execute_task(task, group_id, campaign, commands, agent) -> list:
    ''' Run each command present in the task '''
    external_ids = []
    for command in commands:
        call_worker_api = await call_integration(command.module, command.input, agent.id, agent.integration)
        ExecutedModules.create({**command.dict(), 'task':task, 'campaign':campaign, 'external_id': call_worker_api['external_id'],
            'group_id': group_id, 'agent': agent.id, 'integration': agent.integration})
        external_ids.append({'module': command.module, 'external_id': call_worker_api['external_id']})
    return external_ids

@api.get('/api/v1/scheduler/plan')
async def plan_task_next(next_task: List[PlanTaskIn]):
    ''' Get the next scheduled task and run execution '''
    executed_modules = []
    for task in next_task:
        execute_modules = [ {'agent': agent.id, 'integration':agent.integration, 
        'modules': await execute_task(task.task, task.group_id, task.campaign, task.commands, agent) } for agent in task.agents ]
        executed_modules.append({'group_id': task.group_id, 'task':task.task, 'campaign':task.campaign,
            'executed': execute_modules})
    return executed_modules
