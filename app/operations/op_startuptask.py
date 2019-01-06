from app.models import StartupTasks
import mongoengine


class StartupTask:
    def create(platform, commands, name):
        try:
            new_boot = StartupTasks(
                platform=platform,
                commands=commands,
                name=name
            ).save()

            result = {"result": "success", "data": {"task_id": str(new_boot.id)}}

        except mongoengine.errors.ValidationError:
            result = {"result": "failed", "data": "Task requires explicit commands"}

        except Exception as err:
            result = {"result": "failed", "data": "Unable to add Macro"}

        return result

    def delete(startup_id):
        try:
            startup_object = StartupTasks.objects.get(id=startup_id).delete()
            result = {"result": "success", "data": "Succesfully deleted macro"}

        except mongoengine.errors.DoesNotExist:
            result = {"result": "failed", "message": "Macro does not exist"}

        except Exception as err:
            result = {"result": "failed", "data": "Unable to remove macro"}

        return result

