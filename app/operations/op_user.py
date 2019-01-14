from app.generic import Random
from app.models import Users
import hashlib
import mongoengine
import json

class User:
    def __init__(self, username):
        self.username = username

    def login(self, password):
        try:
            user_object = Users.objects.get(username=self.username)
            db_salt = user_object.salt
            db_password = user_object.password
            complete_pass = db_salt + password
            calc_password = hashlib.sha512(complete_pass.strip().encode('utf-8')).hexdigest()

            if calc_password == db_password:
                return {"result":"success", "data":"Succesfully logged in", "data":user_object}

            else:
                return {"result":"failed", "data":"Username and/or Password incorrect"}

        except mongoengine.errors.DoesNotExist:
            return {"result":"failed", "data":"Username and/or Password incorrect"}


    def get(self):
        try:
            user_object = Users.objects.get(username=self.username)
            result = {'username': user_object['username'], 'groups': [],
                      'email': user_object['email'], 'role': user_object['role'],
                      'id': str(user_object['id'])}

        except mongoengine.errors.DoesNotExist:
            result = {"result": "failed", "message": "User does not exist"}

        except Exception as err:
            result = {"result": "failed", "message": "Gonna' catch them all"}

        return result

    def create(self, password, email, role):
        try:
            salt = Random.create(20)
            password_hash = hashlib.sha512()
            password_string = salt + password
            password_hash.update(password_string.encode('utf-8'))
            password_hash = str(password_hash.hexdigest())

            user = Users(
                username=username, salt=salt, password=password_hash,
                email=email, role = role
            ).save()

            result = {"result": "created", "message": "Succesfully created user"}

        except mongoengine.errors.NotUniqueError:
            result = {"result": "failed", "message": "User already exists"}

        except Exception as err:
            result = {"result": "failed", "message": "Failed to create user"}

        return result

    def delete(self, target_user):
        if self.username == target_user:
            return {"result":"failed", "data":"Unable to remove self from database"}

        try:
            user_object = Users.objects.get(username=self.username).delete()
            result = {"result": "success", "message": "Deleted user from DB"}

        except mongoengine.errors.DoesNotExist:
            result = {"result": "failed", "message": "User does not exist"}


        return result