from app.models import BeaconHistory

class History:
    def __init__(self, beacon_id):
        self.beacon_id = beacon_id
        
    def create(self, platform, username, hostname, data, working_dir, remote_ip):
        try:
            history_object = BeaconHistory(
                beacon_id=self.beacon_id, remote_ip=remote_ip, hostname=hostname,
                data=data, platform=platform, working_dir=working_dir,
                username=username).save()

            result = {"result": "success", "data": "Beacon history succesfully added"}

        except Exception as err:
            result = {"result": "failed", "data": "Unable to add beacon history to database"}

        return result