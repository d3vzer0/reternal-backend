from app import app, api, jwt
from app.runner import celery
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)

class APIWorkers(Resource):
    decorators = []

    def get(self):
        get_workers = celery.send_task('c2.system.workers', retry=True)
        response = get_workers.get()
        return response
        
api.add_resource(APIWorkers, '/api/v1/workers')


class APIWorkerState(Resource):
    decorators = []

    def get(self, worker_name):
        get_workers = celery.send_task('c2.system.workers', retry=True).get()
        # if not worker_name in get_workers: return {'result':'failed', 'data':'Not found'}, 404
        # get_state = celery.send_task(get_workers[worker_name]['state'])
    
        # response = get_workers.get()
        return 'response'
        
api.add_resource(APIWorkerState, '/api/v1/worker/<string:worker_name>')

