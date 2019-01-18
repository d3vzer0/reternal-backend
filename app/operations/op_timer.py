from app.models import Beacons
import mongoengine

class Timer:
    def __init__(self, beacon_id):
        self.beacon_id = beacon_id

    def change(self, new_timer):
        try:
            current_beacon = Beacons.objects.get(beacon_id=self.beacon_id)
            current_beacon.update(set__timer=int(round(new_timer)))
            result = {"result":"success", "data":"Succesfully changed timer"}

        except mongoengine.errors.DoesNotExist:
            result = {"result":"failed", "data":"Beacon does not exist"}

        except Exception as err:
            result = {"result": "failed", "data": "Failed to change timer in DB"}

        return result
