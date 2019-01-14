import mongoengine
from app.models import RevokedTokens

class Token:
    def __init__(self, token):
        self.token = token

    def verify(self):
        try:
            profile = RevokedTokens.objects.get(token=self.token)
            result = True

        except mongoengine.errors.DoesNotExist:
            result = False

        except Exception as err:
            result = False
            
        return result

    def blacklist(self):
        try:
            profile = RevokedTokens(token=self.token).save()
            result = {"result": "success", "message": "Succesfully added token to  blacklist"}

        except mongoengine.errors.NotUniqueError:
            result = {"result": "failed", "message": "Token already exist in blacklist"}

        except Exception as err:
            result = {"result": "failed", "message": "Unable to add token in blacklist"}

        return result

