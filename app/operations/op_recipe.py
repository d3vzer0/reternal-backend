from app.models import Recipes
import mongoengine


class Recipe:
    def __init__(self, recipe):
        self.recipe = recipe
    
    def create(self, commands):
        try:
            new_recipe = Recipes(commands=commands,name=self.recipe).save()
            result = {"result": "success", "data": {"task_id": str(new_recipe.id)}}

        except mongoengine.errors.ValidationError:
            result = {"result": "failed", "data": "Task requires explicit commands"}

        except Exception as err:
            result = {"result": "failed", "data": "Unable to save recipe"}

        return result

    def delete(self):
        try:
            startup_object = Recipes.objects.get(name=self.recipe).delete()
            result = {"result": "success", "data": "Succesfully deleted recipe"}

        except mongoengine.errors.DoesNotExist:
            result = {"result": "failed", "message": "Recipe does not exist"}

        except Exception as err:
            result = {"result": "failed", "data": "Unable to remove recipe"}

        return result

