from app.models import Credentials


class Credential:
    def __init__(self, **kwargs):
          self.kwargs = kwargs

    def create(self):
        try:
            credential = Credentials(source_beacon=self.kwargs['beacon_id'], 
                source_command=self.kwargs['application'], username=self.kwargs['username'], 
                key=self.kwargs['key'], type=self.kwargs['key_type']).save()
            result = {"result": "success", "data": "Successfully added credentials to db"}

        except Exception as err:
            result = {"result": "failed", "data": "Unable to save credentials"}

        return result