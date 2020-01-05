from app.runner import celery
from functools import wraps

def validate_worker(f):
    @wraps(f)
    def worker_decorator(self, *args, **kwargs):
        self.all_workers = celery.send_task('c2.system.workers', retry=True).get()
        if not kwargs['worker_name'] in self.all_workers:
            return {'result':'not_found', 'data':'Worker not found or configured'}, 404
        return f(self, *args, **kwargs)
    return worker_decorator

