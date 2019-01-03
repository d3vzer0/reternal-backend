from app.functions_generic import Generic
from app.models import Users, Commands, Macros, Beacons, BeaconHistory, Tasks, TaskResults
import hashlib
import mongoengine
import json

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



class Result:
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

    def store_result(beacon_id, task_id, command, output, magic_type):
        try:
            taskoutput = TaskResults(
                beacon_id=beacon_id,
                task_id=task_id,
                command=command
            )
            taskoutput.output.put(output, content_type=magic_type)
            taskoutput.save()
            result = {"result": "success", "data": "Succesfully inserted task result"}

        except Exception as err:
            print(err)
            result = {"result": "failed", "data": "Failed to save task results"}

        return result

    def change_timer(beacon_id, new_timer):
        try:
            current_beacon = Beacons.objects.get(beacon_id=beacon_id)
            current_beacon.update(set__timer=int(round(new_timer)))
            result = {"result":"success", "data":"Succesfully changed timer"}

        except mongoengine.errors.DoesNotExist:
            result = {"result":"failed", "data":"Beacon does not exist"}

        except Exception as err:
            result = {"result": "failed", "data": "Failed to change timer in DB"}

        return result

class Task:
    def get(task_id):
        try:
            task_details = Tasks.objects.get(id=task_id)
            result = json.loads(task_details.to_json())

        except mongoengine.errors.DoesNotExist:
            result = {"result":"failed", "data":"Task does not exist"}

        except Exception as err:
            result = {"result": "failed", "data": "Unable to delete task from database"}

        return result

    def delete(task_id):
        try:
            task = Tasks.objects.get(id=task_id).delete()
            result = {"result": "success", "data": "Successfully deleted task"}

        except mongoengine.errors.DoesNotExist:
            result = {"result":"failed", "data":"Task does not exist"}

        except Exception as err:
            result = {"result": "failed", "data": "Unable to delete task from database"}

        return result

    def create(beacon_id, commands, start_date):
        try:
            new_task = Tasks(
                start_date=start_date,
                beacon_id=beacon_id,
                commands=commands
            ).save()

            result = {"result": "success", "data": {"task_id": str(new_task.id)}}

        except mongoengine.errors.ValidationError:
            result = {"result": "failed", "data": "Task requires explicit commands"}

        except Exception as err:
            print(err)
            result = {"result": "failed", "data": "Unable to create task"}

        return result


    def change_state(task_id, state):
        try:
            get_tasks = Tasks.objects(task_id=task_id)
            get_tasks.update(set__task_status=state)
            result = {"result":"success", "data":"Changed task state"}

        except mongoengine.errors.DoesNotExist:
            result = {"result":"failed", "data":"No tasks available"}

        except Exception as err:
            result = {"result":"failed", "data":"Unexpected error"}

        return result


    def process(beacon_id, post_data, beacon_ip):
        try:
            result = {"result":"success", "tasks":[]}
            get_tasks = Tasks.objects(beacon_id=beacon_id, task_status="Open")
            for task in get_tasks:
                commands_list = task.commands
                for command in commands_list:
                    result['tasks'].append({command['name'], command['input'], command['timer']})
                task.update(set__taskStatus="Processing")

        except mongoengine.errors.DoesNotExist:
            result = {"result":"failed", "data":"No tasks available"}

        except Exception as err:
            result = {"result":"failed", "data":"Unexpected error"}

        return result


class Beacon:
    def create(beacon_id, beacon_os, username, timer, hostname, beacon_data, working_dir, remote_ip=""):
        try:
            beacon_object = Beacons(
                beacon_id=beacon_id,
                platform=beacon_os,
                data=beacon_data,
                hostname=hostname,
                username=username,
                working_dir=working_dir,
                remote_ip=remote_ip
            ).save()

            result = {"result": "success", "data": "Beacon succesfully added"}

        except mongoengine.errors.NotUniqueError:
            result = {"result": "failed", "message": "Beacon already exists"}

        except Exception as err:
            result = {"result": "failed",
                      "data": "Unable to add beacon to database"}

        return result

    def pulse(beacon_id, platform, username, hostname, data, working_dir, remote_ip):
        try:
            history_object = BeaconHistory(
                beacon_id=beacon_id,
                remote_ip=remote_ip,
                hostname=hostname,
                data=data,
                platform=platform,
                working_dir=working_dir,
                username=username,
            ).save()

            result = {"result": "success", "data": "Beacon history succesfully added"}

        except Exception as err:
            result = {"result": "failed",
                      "data": "Unable to add beacon history to database"}

        return result

    def results(beacon_id, task_id):
        try:
            pipeline = [{"$lookup": {"from": "task_results", "localField": "_id","foreignField": "task_id", "as": "taskdetails"}}]
            task_aggregation = TaskResults.objects(beacon_id=beacon_id, task_id=task_id).aggregate(*pipeline)
            for output in task_aggregation:
                result = {"beacon_id":output.beacon_id, "type":output.type, "task":output.task, "start_date":str(output.start_date),
                    "task_status":output.task_status, "commands":output.commands, "taskdetails":[]}
                for details in output.taskdetails:
                    if details.content_type == "text/plain":
                        output_url = "/api/result/%s" %(beacon['taskId'])
                        
                    detail = {"id": str(details.id), "end_date":str(output.end_date),}
                    result['taskdetails'].append()

        except mongoengine.errors.DoesNotExist:
            result = {"result":"failed", "data":"No tasks available"}

        return results

 
