from app.models import Beacons, Tasks, TaskResults
import mongoengine

class Result:
    def __init__(self, beacon_id, task_id):
        self.beacon_id = beacon_id
        self.task_id = task_id

    def create(self, command, cmd_type, cmd_input, output, magic_type):
        try:
            taskoutput = TaskResults(
                beacon_id=self.beacon_id, task_id=self.task_id, input=cmd_input,
                type=cmd_type, command=command)
            taskoutput.output.put(output, content_type=magic_type)
            taskoutput.save()
            result = {"result": "success", "data": "Succesfully inserted task result"}

        except Exception as err:
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
