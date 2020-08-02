from app.utils import celery
from app.utils.depends import validate_worker
from celery import Signature

# from app.workers.scheduler import update_task
import pytz

class Scheduler:
    def __init__(self, task, campaign):
        self.task = task
        self.campaign = campaign

    async def _queue_task(self, agent):
        available_workers = await validate_worker(agent.integration)
        execution_process = available_workers[agent.integration]['modules']['run']
        planned_tasks = [ str(celery.send_task(execution_process, args=({'module':module.module, 'input': module.input, 'agent':agent.id},),
            eta=self.task.scheduled_date.astimezone(pytz.utc),
            chain=[Signature('api.scheduler.task.update', kwargs= {'task_context':{
                **module.dict(), 'task': self.task.name, **self.campaign, 'agent': agent.id
            }})])) for module in self.task.commands
        ]
        return planned_tasks

    async def _organise_tasks(self):
        planned_modules = [{'agent': agent.name, 'queue': await self._queue_task(agent)} for agent in self.task.agents]
        return planned_modules