from app.models import Commands, Tasks, TaskResults
import mongoengine
import json

class Task:
    def __init__(self, task_id=None):
        self.task_id = task_id

    def get(self):
        try:
            task_object = Tasks.objects.get(id=self.task_id)
            result = {"result":"success", "data":task_object}

        except mongoengine.errors.DoesNotExist:
            result = {"result":"failed", "data":"Task does not exist"}

        except Exception as err:
            result = {"result": "failed", "data": "Unable to delete task from database"}

        return result

    def delete(self):
        try:
            task = Tasks.objects.get(id=self.task_id).delete()
            result = {"result": "success", "data": "Successfully deleted task"}

        except mongoengine.errors.DoesNotExist:
            result = {"result":"failed", "data":"Task does not exist"}

        except Exception as err:
            result = {"result": "failed", "data": "Unable to delete task from database"}

        return result

    def create(self, beacon_id, commands, start_date, name):
        try:
            new_task = Tasks(
                name=name,
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
