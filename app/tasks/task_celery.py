from celery import Celery
from app.tasks.task_routes import celery_routes
import os

class FlaskCelery:
    def make(app):
        celery = Celery(app.import_name, broker=os.environ["CELERY_BROKER"],
                        backend=os.environ["CELERY_BACKEND"])
        celery.conf.task_routes = celery_routes
        celery.conf.broker_transport_options = {'fanout_prefix': True}
        celery.conf.broker_transport_options = {'fanout_patterns': True}
        TaskBase = celery.Task

        class ContextTask(TaskBase):
            abstract = True

            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return TaskBase.__call__(self, *args, **kwargs)
        celery.Task = ContextTask
        return celery
