from workers import app
from database.models import ExecutedModules

@app.task(name='api.scheduler.task.update')
def update_task(task_response, task_context):
    ExecutedModules.create({**task_context, 'external_id': task_response['response']['external_id']})
    # print(task_response, task_context)

