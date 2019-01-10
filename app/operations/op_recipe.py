from app.models import Recipes
import mongoengine


class Recipe:
    def create(name, commands):
        try:
            new_recipe = Recipes(commands=commands,name=name).save()
            result = {"result": "success", "data": {"task_id": str(new_recipe.id)}}

        except mongoengine.errors.ValidationError:
            result = {"result": "failed", "data": "Task requires explicit commands"}

        except Exception as err:
            result = {"result": "failed", "data": "Unable to save recipe"}

        return result

    def delete(recipe_id):
        try:
            startup_object = Recipes.objects.get(id=recipe_id).delete()
            result = {"result": "success", "data": "Succesfully deleted recipe"}

        except mongoengine.errors.DoesNotExist:
            result = {"result": "failed", "message": "Recipe does not exist"}

        except Exception as err:
            result = {"result": "failed", "data": "Unable to remove recipe"}

        return result

