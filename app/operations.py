import hashlib
import mongoengine
from app.functions_generic import Generic
from app.models import Users, Commands, Macros

class Command:
    def create(name, command_type="default"):
        try:
            commands = Commands(
              name=name,
              type=command_type,
            ).save()
            result = {"result":"success", "message":"Succesfully added command reference to DB"}

        except mongoengine.errors.NotUniqueError:
            result = {"result":"failed", "message":"Command reference already exists"}

        return result

class User:
    def get(user_id):
        try:
            user_object = Users.objects.get(id=user_id)
            result = {'username': user_object['username'], 'groups': [],
                      'email': user_object['email'],
                      'role': user_object['role'],
                      'id': str(user_object['id'])}

        except mongoengine.errors.DoesNotExist:
            result = {"result": "failed", "message": "User does not exist"}

        except:
            result = {"result": "failed", "message": "Gonna' catch them all"}

        return result

    def create(username, password, email, role):
        try:
            salt = Generic.create_random(20)
            password_hash = hashlib.sha512()
            password_string = salt + password
            password_hash.update(password_string.encode('utf-8'))
            password_hash = str(password_hash.hexdigest())

            user = Users(
                username=username,
                salt=salt,
                password=password_hash,
                email=email,
                role = role
            ).save()

            result = {"result": "created",
                      "message": "Succesfully created user"}

        except mongoengine.errors.NotUniqueError:
            result = {"result": "failed", "message": "User already exists"}

        except Exception as err:
            print(err)
            result = {"result": "failed", "message": "Failed to create user"}

        return result

    def delete(user_id):
        try:
            user_object = Users.objects.get(id=user_id).delete()
            result = {"result": "deleted", "message": "Deleted user from DB"}

        except mongoengine.errors.DoesNotExist:
            result = {"result": "failed", "message": "User does not exist"}

        except Exception as err:
            result = {"result": "failed",
                      "message": "Failed to delete user from DB"}

        return result

class Macro:
    def create(username, command_id, macro_name, macro_input):
        try:
            user_object = Users.objects.get(username=username)
           # Todo

        except Exception as err:
            result = {"result": "failed", "data": "Unable to add Macro"}

        return result

    def delete(username, macro_id):
        try:
            userObject = Macros.get(id=macro_id).delete()
            result = {"result": "success", "data": "Succesfully deleted macro"}

        except Exception as err:
            result = {"result": "failed", "data": "Unable to remove macro"}

        return result