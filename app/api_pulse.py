
from app import app, api, celery, jwt
from app.operations import Pulse
from flask import Flask, request, g
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)


class APIPulse(Resource):
    decorators = []

    def __init__(self):
        self.args = reqparse.RequestParser()
        self.args.add_argument('beacon_id', location='json', required=True, help='Beacon ID')
        self.args.add_argument('task_id', location='json', required=False, help='Task ID', type=str)
        parse_args = self.args.parse_args()
        if parse_args["task_id"] is None:
            self.args.add_argument('platform', location='json', required=True, help='Platform', choices=('darwin','windows','linux'))
            self.args.add_argument('username', location='json', required=True, help='Username')
            self.args.add_argument('hostname', location='json', required=True, help='Username')
            self.args.add_argument('data', location='json', required=True, help='Data', type=dict)
            self.args.add_argument('timer', location='json', required=False, help='Timer')
            self.args.add_argument('working_dir', location='json', required=False, help='Working dir')

        else:
            self.args.add_argument('output', location='json', required=True, help='Task Output')
            self.args.add_argument('command', location='json', required=True, help='Command name')
            self.args.add_argument('input', location='json', required=True, help='Command input')
            self.args.add_argument('type', location='json', required=True, help='Command type')


    def post(self):
        platform_mapping = {
            "darwin": "macOS",
            "windows": "Windows",
            "linux": "Linux",
        }
        remote_ip = request.remote_addr
        args = self.args.parse_args()
        if args['task_id'] is None and "platform" in args :
            args['platform'] = platform_mapping[args['platform']]
            result = Pulse.process(args, remote_ip, 'http')
            # result = {"tasks":[]}
        else:
            result = Pulse.result(args['beacon_id'], args['task_id'], args['command'], args['type'], args['input'], args['output'])
        return result

api.add_resource(APIPulse, '/api/v1/ping')
