from app import app, api, jwt
from celery import Signature
from app.runner import celery
from flask import make_response, request
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)
from app.generic import PayloadID
import base64

class APIPayloads(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.payload_types = {
            "windows": {
                "amd64": {"build_state": False, "name": "64Bit Exe" },
                "386": {"build_state": False, "name": "32Bit Exe"} },
            "linux": {
                "amd64": {"build_state": False, "name": "64Bit Bin" },
                "386": {"build_state": False, "name": "32Bit Bin"} },
            "darwin": {
                "amd64": {"build_state": False, "name": "64Bit Elf" },
                "386": {"build_state": False, "name": "32Bit Elf"} } }

    def get(self):
        return self.payload_types

api.add_resource(APIPayloads, '/api/v1/payloads')


class APIPayload(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.args = reqparse.RequestParser()
        if request.method == 'POST':
            self.args.add_argument('platform', location='json', default="darwin", help='Platform', choices=("windows", "linux", "darwin"))
            self.args.add_argument('base_url', location='json', help='Base URL', default=app.config['C2_DEST'])
            self.args.add_argument('arch', location='json', help='Architecture', default="amd64", choices=("amd64", "386"))

        else:
            self.args.add_argument('platform', location='args', default="darwin", help='Platform', choices=("windows", "linux", "darwin"))
            self.args.add_argument('base_url', location='args', help='Base URL', default=app.config['C2_DEST'])
            self.args.add_argument('arch', location='args', help='Architecture', default="amd64", choices=("amd64", "386"))
  
    def post(self):
        args = self.args.parse_args()
        build_id = PayloadID(args.platform, args.arch, args.base_url).create()
        task_chain = celery.send_task(
            'agent.build', args=(args.platform, args.arch, args.base_url, build_id),
            task_id=build_id, link=[ Signature('api.buildstate', immutable=True, queue='api', 
            args=(args.platform, args.arch, args.base_url))])

        response = {'platform':args.platform, 'arch':args.arch, 'build_id':build_id,
            'base_url':args.base_url}
        return response

    
    def get(self):
        args = self.args.parse_args()
        build_id = PayloadID(args.platform, args.arch, args.base_url).create()
        task_state = celery.AsyncResult(build_id).state
        response = {'platform':args.platform, 'arch':args.arch, 'build_id':build_id,
                'base_url':args.base_url, 'state':task_state}
        return response
   
api.add_resource(APIPayload, '/api/v1/payload')


class APIGetPayload(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.args = reqparse.RequestParser()
        self.args.add_argument('platform', location='args', default="darwin", help='Platform', choices=("windows", "linux", "darwin"))
        self.args.add_argument('base_url', location='args', help='Base URL', default=app.config['C2_DEST'])
        self.args.add_argument('arch', location='args', help='Architecture', default="amd64", choices=("amd64", "386"))
    
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
        
api.add_resource(APIGetPayload, '/api/v1/payload/get')

