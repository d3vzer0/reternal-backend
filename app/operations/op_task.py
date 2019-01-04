from app.models import Commands, Tasks, TaskResults
import mongoengine
import json

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

