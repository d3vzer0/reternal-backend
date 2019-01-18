from app import celery

class ResponseSocket:
    def __init__(self, task_id):
        self.task_id = task_id

    def respond(self, command, cmd_type, cmd_input, output, magic_type):
        if magic_type == 'text/plain' or command == 'exec_shell':
            result = {'task_id':self.task_id, 'command':command, 'data':output.decode('utf-8'), 'magic':magic_type}
        else:
            result = {'task_id':self.task_id, 'command':command, 'magic':magic_type}

        send_result = celery.send_task('api.result', retry=True, args=(result,))
        return {'result':'success', 'data':str(send_result)}