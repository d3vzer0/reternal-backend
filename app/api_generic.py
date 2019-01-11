import hashlib
import random
import json
from app import app, api, celery, jwt
from app.models import Users
from app.operations import User, RevokeToken
from app.validators import Authentication, Permissions
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
    is_revoked = Authentication.blacklist(jti)
    return is_revoked


class APILogin(Resource):
    def __init__(self):
        self.args = reqparse.RequestParser()
        self.username = self.args.add_argument('username', location='json', required=True, help='Username')
        self.password = self.args.add_argument('password', location='json', required=True, help='Password')

    def post(self):
        args = self.args.parse_args()
        validate = Authentication.login(args['username'], args['password'])
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
        revoke_token = RevokeToken.create(jti)
        return revoke_token

api.add_resource(APILogoutRefresh, '/api/v1/logout/refresh')


class APILogout(Resource):
    decorators = [jwt_required]
    def get(self):
        jti = get_raw_jwt()['jti']
        revoke_token = RevokeToken.create(jti)
        return revoke_token

api.add_resource(APILogout, '/api/v1/logout/token')


class APIUsers(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.args = reqparse.RequestParser()
        if request.method == "POST":
            self.args.add_argument('username', location='json', required=True, help='Username')
            self.args.add_argument('password', location='json', required=True, help='Password')
            self.args.add_argument('email', location='json',required=True, help='Username')

    def post(self):
        args = self.args.parse_args()
        operation = User().create(args['username'], args['password'],args['email'])
        return operation

    def get(self):
        users_objects = Users.objects().to_json()
        result = json.loads(users_object)
        return result


api.add_resource(APIUsers, '/api/v1/users')


class APISesion(Resource):
    decorators = [jwt_required]
    def get(self):
        claims = get_jwt_claims()
        return {"username":get_jwt_identity(), "role":get_jwt_claims()['role']}

api.add_resource(APISesion, '/api/v1/session')


class APIUser(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.args = reqparse.RequestParser()
        if request.method == "POST":
            self.args.add_argument('password', location='json', required=False)
            self.args.add_argument('email', location='json',required=False)

    def get(self, user_id=None):
        if user_id is None:
            user_id = str(g.currentUser.id)
        get_user = User().get(user_id)
        return get_user

    def delete(self, user_id=None):
        if user_id is None:
            result = {"result": "failed", "message": "Requires user ID"}
        else:
            current_user = str(g.currentUser.id)
            validate_admin = Permissions.delete_user(current_user, user_id)
            if validate_admin['result'] == "success":
                result = User().delete(user_id)
            else:
                result = validate_admin

        return result

    def post(self, user_id):
        args = self.args.parse_args()


api.add_resource(APIUser, '/api/v1/user', '/api/v1/user/<string:user_id>')
