from app import app
from app.models import Users, Beacons, Commands, Tasks
import mongoengine
import re

class Existance:
    def user(username):
        try:
            user_details = Users.objects.get(username=username)
            return {"result":"failed", "data":"User already exist"}

        except mongoengine.errors.DoesNotExist:
            return {"result":"success", "data":"User does exists exist"}


    def command(command_name):
        if re.match(r'^[A-Za-z0-9_]+$', command_name):
            try:
                print(command_name)
                command_details = Commands.objects.get(name=command_name)
                return {"result":"exists", "data":str(command_details.id)}

            except mongoengine.errors.DoesNotExist:
                return {"result":"failed", "data":"Command does not exist"}
        else:
            return {"result":"failed", "data":"Command names can only have alphanumeric chars and underscores"}

    def beacon(beacon_id):
        try:
            beacon_object = Beacons.objects.get(beacon_id=beacon_id)
            return {"result":"success", "data":"Beacon exists"}

        except mongoengine.errors.DoesNotExist:
            return {"result":"failed", "data":"Beacon does not exist"}


    def task(beacon_id, task_id):
        try:
            verify_task = Tasks.objects.get(beacon_id=beacon_id, id=task_id)
            result = {"result":"success", "data":"Beacon has tasks available"}

        except mongoengine.errors.DoesNotExist:
            result = {"result":"failed", "data":"No tasks available for beacon"}

        except Exception as err:
            print(err)
            result = {"result":"failed", "data":"Unexpected error"}

        return result