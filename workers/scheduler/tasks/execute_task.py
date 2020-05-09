from workers import app

@app.task(name='api.scheduler.task.update')
def update_task(task_response):
    print(task_response)