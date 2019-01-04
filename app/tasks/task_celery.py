from celery import Celery

class FlaskCelery:
    def make(app):
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
