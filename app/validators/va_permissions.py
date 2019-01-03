
from app import app
from app.models import Users
import mongoengine


class Permissions:
    def create_user(username, email, role):
        if role not in ['Administrator', 'User', 'Privileged']:
            return {"result":"failed", "data":"Invalid Role selected for user"}

        try:
            userDetails = Users.objects.get(username=username)
            return {"result":"failed", "data":"User already exists"}

        except mongoengine.errors.DoesNotExist:
            return {"result":"success", "data":"User does not exist"}

    def delete_user(ownuser, username):
        if username == ownuser:
            return {"result":"failed", "data":"Unable to remove self from database"}

        try:
            Users.objects.get(username=username)
            return {"result":"success", "data":"User exist"}

        except mongoengine.errors.DoesNotExist:
            return {"result":"failed", "data":"Target user does not exist in the system"}

    def administrator(username):
        try:
            permissions = Users.objects(user=username, role="administrator")
            return {"result":"success", "data":"User has sufficient rights to update projects"}

        except mongoengine.errors.DoesNotExist:
            return {"result":"failed", "data":"Project does not exist or user does not have proper permissions"}
