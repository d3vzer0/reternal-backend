from app.models import Beacons, BeaconHistory, TaskResults, Tasks
import mongoengine


class Beacon:
    def __init__(self, beacon_id):
        self.beacon_id = beacon_id

    def get(self):
        try:
            beacon_object = Beacons.objects.get(beacon_id=self.beacon_id)
            result = {"result":"success", "data":"Beacon exists"}

        except mongoengine.errors.DoesNotExist:
            result = {"result":"failed", "data":"Beacon does not exist"}

        except Exception as err:
            result = {"result":"failed", "data":"Unable to query beacon"}

        return result


    def create(self, beacon_os, username, timer, hostname, beacon_data, working_dir, remote_ip=""):
        try:
            beacon_object = Beacons(
                beacon_id=self.beacon_id, platform=beacon_os,
                data=beacon_data, hostname=hostname, username=username,
                working_dir=working_dir, remote_ip=remote_ip
            ).save()

            result = {"result": "success", "data": "Beacon succesfully added"}

        except mongoengine.errors.NotUniqueError:
            result = {"result": "failed", "message": "Beacon already exists"}

        except Exception as err:
            result = {"result": "failed", "data": "Unable to add beacon to database"}

        return result

    def results(self, beacon_id, task_id):
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

 