from app.models import Beacons, Tasks, TaskResults
from app.sockets import ResponseSocket
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
            ResponseSocket(self.task_id).respond(command, cmd_type, cmd_input, output, magic_type)
            result = {"result": "success", "data": "Succesfully inserted task result"}

        except Exception as err:
            result = {"result": "failed", "data": "Failed to save task results"}

        return result

