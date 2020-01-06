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
   
api.add_resource(APIPayloads, '/api/v1/stagers/<string:worker_name>')


class APIPayload(Resource):
    decorators = [jwt_required]

   
    
    def get(self):
        args = self.args.parse_args()
        build_id = PayloadID(args.platform, args.arch, args.base_url).create()
        task = celery.AsyncResult(build_id)

        if task.state == 'PENDING': return '', 204
        build_agent = task.get()
        build_agent_binary = base64.b64decode(build_agent["file"])
        build_agent_name = "reternal-%s-%s" %(args.platform, args.arch)
        response = make_response(build_agent_binary)
        response.headers.set('Content-Type', 'application/octet-stream')
        response.headers.set('Content-Disposition', 'attachment', filename=build_agent_name)
        return response
        
api.add_resource(APIPayload, '/api/v1/payload/get')

