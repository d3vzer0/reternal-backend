from app import api, celery
from app.utils.depends import validate_worker
from workers.scheduler import update_task
import pytz

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