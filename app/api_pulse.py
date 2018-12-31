
from app import app, api, celery, jwt
from app.functions_pulse import Pulse
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
        self.args.add_argument('platform', location='json', required=True, help='Platform')
        self.args.add_argument('username', location='json', required=True, help='Username')
        self.args.add_argument('hostname', location='json', required=True, help='Username')
        self.args.add_argument('data', location='json', required=True, help='Data', type=dict)
        self.args.add_argument('tasks', location='json', required=False, help='Data', type=dict)
        self.args.add_argument('timer', location='json', required=False, help='Timer')

    def post(self):
        args = self.args.parse_args()
        remote_ip = request.remote_addr
        result = Pulse.process(args, remote_ip, 'http')
        return result

api.add_resource(APIPulse, '/api/v1/ping')
