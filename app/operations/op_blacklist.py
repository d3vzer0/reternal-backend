import mongoengine
from app.models import RevokedTokens

class RevokeToken:
    def create(token):
        try:
            profile = RevokedTokens(token=token).save()
            result = {"result": "success", "message": "Succesfully added token to  blacklist"}

        except mongoengine.errors.NotUniqueError:
            result = {"result": "failed", "message": "Token already exist in blacklist"}

        except Exception as err:
            result = {"result": "failed", "message": "Unable to add token in blacklist"}

        return result

