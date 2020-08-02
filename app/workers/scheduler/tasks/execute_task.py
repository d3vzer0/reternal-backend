from app.workers import celery
from app.database.models import ExecutedModules

@celery.task(name='api.scheduler.task.update')
def update_task(task_response, task_context=None):
    ExecutedModules.create({**task_context, 'external_id': task_response['response']['external_id']})
    # print(task_response, task_context)

