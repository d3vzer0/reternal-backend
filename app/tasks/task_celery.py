from celery import Celery
from app.tasks.task_routes import celery_routes

class FlaskCelery:
    def __init__(self, app):
        self.app = app

    def make(self):
        celery = Celery(self.app.import_name, broker=self.app.config['CELERY_BROKER'],
                        backend=self.app.config['CELERY_BACKEND'])
        celery.conf.task_routes = celery_routes
        celery.conf.broker_transport_options = {'fanout_prefix': True}
        celery.conf.broker_transport_options = {'fanout_patterns': True}
        return celery
