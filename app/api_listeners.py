from app import app, api, jwt
from app.runner import celery
from app.decorators.validworkers import validate_worker
from flask import request
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)

class APIListeners(Resource):
    decorators = []

    @validate_worker
    def get(self, worker_name):
        get_listeners = celery.send_task(self.all_workers[worker_name]['listeners']['get'],
            retry=True).get()
        return get_listeners

    @validate_worker
    def post(self, worker_name, listener_type):
        create_listener = celery.send_task(self.all_workers[worker_name]['listeners']['create'],
            args=(listener_type, request.get_json(),), retry=True).get()
        return create_listener

api.add_resource(APIListeners, '/api/v1/listeners/<string:worker_name>',
    '/api/v1/listeners/<string:worker_name>/<string:listener_type>')


class APIListener(Resource):
    decorators = []

    @validate_worker
    def delete(self, worker_name, listener_name):
        delete_listener = celery.send_task(self.all_workers[worker_name]['listeners']['delete'],
            args=(listener_name,), retry=True).get()
        return delete_listener

api.add_resource(APIListener, '/api/v1/listener/<string:worker_name>/<string:listener_name>')


class APIListenerOptions(Resource):
    decorators = []

    @validate_worker
    def get(self, worker_name):
        get_listeners = celery.send_task(self.all_workers[worker_name]['listeners']['options'],
            retry=True).get()
        return get_listeners

api.add_resource(APIListenerOptions, '/api/v1/listeners/options/<string:worker_name>')
