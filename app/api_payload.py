from app import app, api, jwt
from celery import Signature
from app.runner import celery
from flask import make_response, request
from app.decorators.validworkers import validate_worker
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)
import base64


class APIPayloads(Resource):
    decorators = []

    @validate_worker    
    def get(self, worker_name):
        get_stagers = celery.send_task(self.all_workers[worker_name]['stagers']['get'],
            retry=True).get()
        return get_stagers


    @validate_worker
    def post(self, worker_name):
        create_listener = celery.send_task(self.all_workers[worker_name]['stagers']['create'],
            args=(request.get_json(),), retry=True).get()
        return create_listener
   
api.add_resource(APIPayloads, '/api/v1/stagers/<string:worker_name>')
