from app.models import Macros
import mongoengine


class Macro:
    def create(name, command, input):
        try:
            macro_object = Macros(
               name=name,
               command=command,
               input=input
            ).save()

            result = {"result": "success", "message": "Macro created"}

        except mongoengine.errors.NotUniqueError:
            result = {"result": "failed", "message": "Macro already exists"}

        except Exception as err:
            result = {"result": "failed", "data": "Unable to add Macro"}

        return result

    def delete(macro_id):
        try:
            userObject = Macros.get(id=macro_id).delete()
            result = {"result": "success", "data": "Succesfully deleted macro"}

        except mongoengine.errors.DoesNotExist:
            result = {"result": "failed", "message": "Macro does not exist"}

        except Exception as err:
            result = {"result": "failed", "data": "Unable to remove macro"}

        return result

