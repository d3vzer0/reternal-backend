from app import app
from app import db
from app.models import *
import datetime, hashlib, random,json, re
from email.utils import parseaddr


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

        except db.DoesNotExist:
            return {"result":"failed", "data":"Username and/or Password incorrect"}


class Existance:
    def user(username):
        try:
            user_details = Users.objects.get(username=username)
            return {"result":"failed", "data":"User already exist"}

        except db.DoesNotExist:
            return {"result":"success", "data":"User does exists exist"}


    def command(command_id):
        if re.match(r'^[A-Za-z0-9_]+$', command_id):
            try:
                command_details = Commands.objects.get(id=command_id)
                return {"result":"exists", "data":str(command_details.id)}

            except db.DoesNotExist:
                return {"result":"unique", "data":"Command does not exist"}
        else:
            return {"result":"failed", "data":"Command names can only have alphanumeric chars and underscores"}

    def beacon(beacon_id):
        try:
            beacon_object = Beacons.objects.get(beacon_id=beacon_id)
            return {"result":"success", "data":"Beacon exists"}

        except db.DoesNotExist:
            return {"result":"failed", "data":"Beacon does not exist"}

    def tasks(beacon_id, post_data, beacon_ip):
        try:
            result = {"result":"success", "tasks":[]}
            get_tasks = Tasks.objects(beacon_id=beacon_id, task_status="Open")
            for task in get_tasks:
                commands_list = task.commands
                for command in commands_list:
                    result['tasks'].append({command['name'], command['input'], command['timer']})
                task.update(set__taskStatus="Processing")

        except db.DoesNotExist:
            result = {"result":"failed", "data":"No tasks available"}

        except Exception as err:
            result = {"result":"failed", "data":"Unexpected error"}

        return result


class Permissions:
    def create_user(username, email, role):
        if role not in ['Administrator', 'User', 'Privileged']:
            return {"result":"failed", "data":"Invalid Role selected for user"}

        try:
            userDetails = Users.objects.get(username=username)
            return {"result":"failed", "data":"User already exists"}

        except db.DoesNotExist:
            return {"result":"success", "data":"User does not exist"}

    def delete_user(ownuser, username):
        if username == ownuser:
            return {"result":"failed", "data":"Unable to remove self from database"}

        try:
            Users.objects.get(username=username)
            return {"result":"success", "data":"User exist"}

        except db.DoesNotExist:
            return {"result":"failed", "data":"Target user does not exist in the system"}

    def administrator(username):
        try:
            permissions = Users.objects(user=username, role="administrator")
            return {"result":"success", "data":"User has sufficient rights to update projects"}

        except db.DoesNotExist:
            return {"result":"failed", "data":"Project does not exist or user does not have proper permissions"}
