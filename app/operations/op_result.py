from app.models import Beacons, Tasks, TaskResults
import mongoengine

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

    def store_result(beacon_id, task_id, command, cmd_type, cmd_input, output, magic_type):
        try:
            taskoutput = TaskResults(
                beacon_id=beacon_id,
                input=cmd_input,
                type=cmd_type,
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
