import random
import string
from celery import Celery


class Generic:
    def create_random(size):
        random_result = ''.join([random.choice(
                                string.ascii_letters + string.digits)
                                for n in range(size)])
        return random_result


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'],
                    backend=app.config['result_backend'])
    celery.conf.broker_transport_options = {'fanout_prefix': True}
    celery.conf.broker_transport_options = {'fanout_patterns': True}
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery
