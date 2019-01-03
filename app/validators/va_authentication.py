from app import app
from app.models import Users
import hashlib
import mongoengine


class Authentication:
    def login(username, password):
        try:
            user_object = Users.objects.get(username=username)
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
