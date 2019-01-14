from app.models import Commands
import mongoengine

class Command:
    def __init__(self, command):
        self.command = command

    def create(self, command_type="manual"):
        try:
            commands = Commands(name=self.command, type=command_type).save()
            result = {"result":"success", "message":"Succesfully added command reference to DB"}

        except mongoengine.errors.NotUniqueError:
            result = {"result":"failed", "message":"Command reference already exists"}

        except Exception as err:
            result = {"result": "failed", "message": "Error querying DB"}

        return result

    def get(self):
        try:
            commands = Commands.objects.get(name=self.command, type=command_type).save()
            result = {"result":"success", "data":commands}

        except mongoengine.errors.DoesNotExist:
            result = {"result": "failed", "message": "Command does not exist"}

        except Exception as err:
            result = {"result": "failed", "message": "Error querying DB"}
