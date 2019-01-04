from app import app, api, celery, jwt
from flask import make_response
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)
import shlex
import subprocess
import hashlib
import os
import base64

class APIPayloads(Resource):
    decorators = []

    def get(self):
        payload_types = [
            {"platform": "windows", "types":[
                {"arch":"amd64", "name":"64Bit Exe"},
                {"arch":"386", "name":"32Bit Exe"}]},
            {"platform": "linux", "types":[
                {"arch":"amd64", "name":"64Bit ELF"},
                {"arch":"386", "name":"32Bit ELF"}]},
            {"platform": "darwin", "types":[
                {"arch":"amd64", "name":"64Bit BIN"},
                {"arch":"386", "name":"32Bit BIN"}]}
            ]

        return payload_types

api.add_resource(APIPayloads, '/api/v1/payloads')



class APIPayload(Resource):
    decorators = []


    def __init__(self):
        self.args = reqparse.RequestParser()
        self.args.add_argument('platform', location='args', default="darwin", help='Platform', choices=("windows", "linux", "darwin"))
        self.args.add_argument('base_url', location='args', help='Base URL', default="http://localhost:5000")
        self.args.add_argument('arch', location='args', help='Architecture', default="amd64", choices=("amd64", "386"))

  
    def get(self):
        args = self.args.parse_args()
        escaped_url = shlex.quote(args.base_url)
        combined_id = "%s%s%s" %(args.platform,args.arch,escaped_url)
        build_id = hashlib.sha1(combined_id.encode('utf-8')).hexdigest()
        build_agent = celery.send_task('agent.build', retry=True,
            args=(args.platform, args.arch, args.base_url, build_id), 
            kwargs={}, task_id=build_id).get()
        
        build_agent_binary = base64.b64decode(build_agent["file"])
        build_agent_name = "reternal-%s-%s" %(args.platform, args.arch)
        response = make_response(build_agent_binary)
        response.headers.set('Content-Type', 'application/octet-stream')
        response.headers.set('Content-Disposition', 'attachment', filename=build_agent_name)
        return response
   

api.add_resource(APIPayload, '/api/v1/payload')

