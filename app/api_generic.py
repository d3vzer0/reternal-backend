import hashlib
import random
import json
import pyotp
from functools import wraps
from app import app, api, jwt
from app.models import Users
from app.operations import User, Token
from flask import Flask, request, g
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims,
    get_raw_jwt, jwt_refresh_token_required,
    create_refresh_token
)


@jwt.user_claims_loader
def add_claims_to_access_token(user):
    result = {'role':user.role}
    return result


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.username


@jwt.expired_token_loader
def expired_token_callback():
    result = {'status':401, 'sub_status':42, 'data':'Token expired'}
    return json.dumps(result), 401


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    is_revoked = Token.verify(jti)
    return is_revoked



class APILogin(Resource):
    def __init__(self):
        self.args = reqparse.RequestParser()
        self.username = self.args.add_argument('username', location='json', required=True, help='Username')
        self.password = self.args.add_argument('password', location='json', required=True, help='Password')

    def post(self):
        args = self.args.parse_args()
        validate = User(args.username).login(args.password)
        if validate['result'] == 'success':
            username = str(validate['data'].username)
            access_token = create_access_token(identity=validate['data'])
            refresh_token = create_refresh_token(identity=validate['data'])
            result = {"access_token":access_token, "refresh_token":refresh_token}
            return result

        else:
            return validate, 401


api.add_resource(APILogin, '/api/v1/login')


class APIRefresh(Resource):
    decorators = [jwt_refresh_token_required]
    def get(self):
        user_object = Users.objects.get(username=get_jwt_identity())
        access_token = create_access_token(identity=user_object)
        result = {"access_token":access_token}
        return result

api.add_resource(APIRefresh, '/api/v1/refresh') 



class APILogoutRefresh(Resource):
    decorators = [jwt_refresh_token_required]
    def get(self):
        jti = get_raw_jwt()['jti']
        revoke_token = Token(jti).blacklist()
        return revoke_token

api.add_resource(APILogoutRefresh, '/api/v1/logout/refresh')


class APILogout(Resource):
    decorators = [jwt_required]
    def get(self):
        jti = get_raw_jwt()['jti']
        revoke_token = Token(jti).blacklist()
        return revoke_token

api.add_resource(APILogout, '/api/v1/logout/token')

ROLEOPTIONS = ('User', 'Admin')
class APIUsers(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.args = reqparse.RequestParser()
        if request.method == "POST":
            self.args.add_argument('username', location='json', required=True, help='Username')
            self.args.add_argument('password', location='json', required=True, help='Password')
            self.args.add_argument('role', location='json', required=True, help='Role', choices=ROLEOPTIONS)

    def post(self):
        args = self.args.parse_args()
        operation = User(args['username']).create(args['password'], args['role'])
        return operation

    def get(self):
        users_object = Users.objects().only('id', 'username', 'role')
        users_count = users_object.count()
        users_data = json.loads(users_object.to_json())
        result = {'count':users_count, 'data':users_data}
        return result


api.add_resource(APIUsers, '/api/v1/users')


class APISesion(Resource):
    decorators = [jwt_required]
    def get(self):
        claims = get_jwt_claims()
        result = {'username':get_jwt_identity(), 'role': get_jwt_claims()['role']}
        return result

api.add_resource(APISesion, '/api/v1/session')


class APIUser(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.current_user = get_jwt_identity()
        self.role = get_jwt_claims()['role']
        self.args = reqparse.RequestParser()
        if request.method == "POST":
            self.args.add_argument('password', location='json', required=False)
            self.args.add_argument('role', location='json',required=False)

    def delete(self, target_user):
        if self.role == 'Admin':
            result = User(self.current_user).delete(target_user)
        else:
            result = {'result':'failed', 'data':'Insufficient permissions', 'status': 401}

        return result, result['status']

    def post(self, target_user):
        args = self.args.parse_args()
        if self.role == 'Admin' or target_user == self.current_user:
            result = User(self.current_user).change(target_user, args['role'], args['password'])
        else:
            result = {'result':'failed', 'data':'Insufficient permissions', 'status': 401}

        return result, result['status']

    def get(self, target_user):
        if self.role == 'Admin' or target_user == self.current_user:
            prov_url = "%s@reternal" %(self.current_user)
            user_object = User(target_user).get()
            otp_prov = pyotp.totp.TOTP(user_object['data'].otp).provisioning_uri(prov_url, issuer_name="ReternalAPI") 
            result = {'result':'success', 'data':otp_prov, 'status':200}
        else:
            result = {'result':'failed', 'data':'Insufficient permissions', 'status': 401}

        return result


api.add_resource(APIUser, '/api/v1/user/<string:target_user>')
