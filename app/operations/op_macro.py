from app.functions_generic import Generic
from app.models import Users, Macros
import mongoengine


class Macro:
    def create(username, command_id, macro_name, macro_input):
        try:
            user_object = Users.objects.get(username=username)
           # Todo

        except mongoengine.errors.NotUniqueError:
            result = {"result": "failed", "message": "Macro already exists"}

        except Exception as err:
            result = {"result": "failed", "data": "Unable to add Macro"}

        return result

    def delete(username, macro_id):
        try:
            userObject = Macros.get(id=macro_id).delete()
            result = {"result": "success", "data": "Succesfully deleted macro"}

        except mongoengine.errors.DoesNotExist:
            result = {"result": "failed", "message": "Macro does not exist"}

        except Exception as err:
            result = {"result": "failed", "data": "Unable to remove macro"}

        return result

