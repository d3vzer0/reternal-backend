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
                return {"result":"success", "data":"Succesfully logged in", "data":user_object, "status": 200}

            else:
                return {"result":"failed", "data":"Username and/or Password incorrect", "status": 400}

        except mongoengine.errors.DoesNotExist:
            return {"result":"failed", "data":"Username and/or Password incorrect", "status": 403}


    def get(self):
        try:
            user_object = Users.objects.get(username=self.username)
            result = {"result": "success", "data": user_object, "status": 200}

        except mongoengine.errors.DoesNotExist:
            result = {"result": "failed", "data": "User does not exist", "status": 403}

        except Exception as err:
            result = {"result": "failed", "data": "Unable to fetch user", "status": 500}

        return result

    def create(self, password, role):
        if len(password) < 10:
            result = {"result": "failed", "data": "Password length is too short", "status": 400}
            return result

        try:
            salt = Random.create(20)
            password_hash = hashlib.sha512()
            password_string = salt + password
            password_hash.update(password_string.encode('utf-8'))
            password_hash = str(password_hash.hexdigest())

            user = Users(username=self.username, salt=salt, password=password_hash, role = role).save()
            result = {"result": "created", "data": "Succesfully created user", "status": 200}

        except mongoengine.errors.NotUniqueError:
            result = {"result": "failed", "data": "User already exists", "status": 409}

        except Exception as err:
            result = {"result": "failed", "data": "Failed to create user", "status": 500}

        return result

    def change(self, target_user, role, password):
        try:
            user_object = Users.objects.get(username=target_user)
            if len(password) > 0 and len(password) < 10:
                result = {"result": "failed", "data": "Password length is too short", "status": 400}
                return result  
            
            if len(password) == 0:
                salt = user_object['salt']
                password_hash = user_object['password']
 
            else:
                salt = Random.create(20)
                password_hash = hashlib.sha512()
                password_string = salt + password
                password_hash.update(password_string.encode('utf-8'))
                password_hash = str(password_hash.hexdigest())

            user_object.update(salt=salt, password=password_hash, role=role)
            result = {"result": "success", "data": "Succesfully changed user", "status": 200}

        except mongoengine.errors.DoesNotExist:
            result = {"result": "failed", "data": "User does not exists", "status": 403}

        except Exception as err:
            result = {"result": "failed", "data": "Failed to change user", "status": 500}

        return result

    def delete(self, target_user):
        if self.username == target_user:
            return {"result":"failed", "data":"Unable to remove self from database"}

        try:
            user_object = Users.objects.get(username=target_user).delete()
            result = {"result": "success", "data": "Deleted user from DB", "status": 200}

        except mongoengine.errors.DoesNotExist:
            result = {"result": "failed", "data": "User does not exist", "status": 403}


        return result