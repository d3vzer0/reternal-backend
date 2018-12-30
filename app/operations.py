import hashlib
import mongoengine
from app.functions_generic import Generic
from app.models import Users, Commands, Macros, Beacons, BeaconHistory


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

        except Exception as err:
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
            result = {"result": "failed", "message": "Failed to create user"}

        return result

    def delete(user_id):
        try:
            user_object = Users.objects.get(id=user_id).delete()
            result = {"result": "deleted", "message": "Deleted user from DB"}

        except mongoengine.errors.DoesNotExist:
            result = {"result": "failed", "message": "User does not exist"}


        return result


class Macro:
    def create(username, command_id, macro_name, macro_input):
        try:
            user_object = Users.objects.get(username=username)
           # Todo

        except mongoengine.errors.NotUniqueError:
            result = {"result": "failed", "message": "Macro already exists"}

        except Exception as err:
            result = {"result": "failed", "data": "Unable to add Macro"}

        return result

    def delete(username, macro_id):
        try:
            userObject = Macros.get(id=macro_id).delete()
            result = {"result": "success", "data": "Succesfully deleted macro"}

        except mongoengine.errors.DoesNotExist:
            result = {"result": "failed", "message": "Macro does not exist"}

        except Exception as err:
            result = {"result": "failed", "data": "Unable to remove macro"}

        return result


class Task:
    def delete(task_id):
        try:
            task = Tasks.objects.get(id=task_id).delete()
            result = {"result": "success", "data": "Successfully deleted task"}

        except Exception as err:
            result = {"result": "failed", "data": "Unable to delete task from database"}

        return result

    def create(beacon_id, task_name, cmd_input, task_type):
        try:
            new_task = Tasks(
                beacon_id=beacon_id,
                type=task_type,
                start_date=datetime.datetime.now(),
            ).save()

            result = {"result": "success", "data": {"taskid": task_id,
                      "beacon": beacon_id}}

        except mongoengine.errors.NotUniqueError:
            result = {"result": "failed", "message": "Task already exists"}

        except Exception as e:
            result = {"result": "failed",
                      "data": "Unable to update/write database"}

        return result

    def change_timer(beacon_id, new_timer):
        try:
            current_beacon = Beacons.objects.get(beacon_id=beacon_id)
            current_beacon.update(set__timer=int(round(new_timer)))
            result = {"result":"success", "data":"Succesfully changed timer"}

        except mongoengine.errors.DoesNotExist:
            result = {"result":"failed", "data":"Beacon does not exist"}

        return result


    def store_result(beacon_id, task_id, task_end, task_out, task_mime):
        try:
            taskoutput = TaskResults(
                beacon_id=beacon_id,
                task_id=task_id,
                end_date=task_end,
            )
            taskoutput.output.put(task_out, content_type=task_mime)
            taskoutput.save()
            result = {"result": "success",
                      "data": "Succesfully inserted task result"}

        except Exception as e:
            result = {"result": "failed", "data": "Failed to save task results"}

        return result


class Beacon:
    def create(beacon_id, beacon_os, username, timer, beacon_data, remote_ip=""):
        try:
            beacon_object = Beacons(
                beacon_id=beacon_id,
                platform=beacon_os,
                data=beacon_data,
                username=username,
                remote_ip=remote_ip
            ).save()

            result = {"result": "success", "data": "Beacon succesfully added"}

        except mongoengine.errors.NotUniqueError:
            result = {"result": "failed", "message": "Beacon already exists"}

        except Exception as err:
            result = {"result": "failed",
                      "data": "Unable to add beacon to database"}

        return result

    def pulse(beacon_id, platform, username, data, remote_ip):
        try:
            history_object = BeaconHistory(
                beacon_id=beacon_id,
                remote_ip=remote_ip,
                data=data,
                platform=platform,
                username=username,
            ).save()

            result = {"result": "success",
                      "data": "Beacon history succesfully added"}

        except Exception as err:
            print(err)

            result = {"result": "failed",
                      "data": "Unable to add beacon history to database"}

        return result

    def store_creds(beacon_id, application, username, key, key_type):
        try:
            credential = Credentials(
                source_beacon=beacon_id,
                source_command=application,
                username=username,
                key=key,
                type=key_type,
            ).save()
            result = {"result": "success",
                      "data": "Successfully added credentials to db"}

        except Exception as err:
            result = {"result": "failed", "data": "Unable to save credentials"}

        return result
