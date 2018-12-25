from app import app
from app import db
from app.models import *
import datetime, hashlib, random,json, re
from email.utils import parseaddr


class Authentication:
    def login(username, password):
        try:
            userAuth = Users.objects.get(username=username)
            dbSalt = userAuth.salt
            dbPassword = userAuth.password
            completePass = dbSalt + password
            calcPassword = hashlib.sha512(completePass.strip().encode('utf-8')).hexdigest()

            if calcPassword == dbPassword:
                return {"result":"success", "data":"Succesfully logged in"}

            else:
                return {"result":"failed", "data":"Username and/or Password incorrect"}

        except db.DoesNotExist:
            return {"result":"failed", "data":"Username and/or Password incorrect"}


class Existance:
    def user(username):
        try:
            userDetails = Users.objects.get(username=username)
            return {"result":"failed", "data":"User already exist"}

        except db.DoesNotExist:
            return {"result":"success", "data":"User does exists exist"}

    def project(projectname):
        try:
            projectDetails = Projects.objects.get(projectname=projectname)
            return {"result":"failed", "data":"Project already exists"}

        except db.DoesNotExist:
            return {"result":"success", "data":"Project does not exist"}

    def command(commandIdentifier):
        if re.match(r'^[A-Za-z0-9_]+$', commandIdentifier):
            try:
                commandDetails = Commands.objects.get(commandIdentifier=commandIdentifier)
                return {"result":"exists", "data":str(commandDetails.id)}

            except db.DoesNotExist:
                return {"result":"unique", "data":"Command does not exist"}
        else:
            return {"result":"failed", "data":"Command names can only have alphanumeric chars and underscores"}

    def beacon(beaconid):
        try:
            getRelavance = Beacons.objects.get(beaconId=beaconid)
            return {"result":"success", "data":"Beacon exists"}

        except db.DoesNotExist:
            return {"result":"failed", "data":"Beacon does not exist"}


    def membership(username, projectname):
        try:
            userObject = Users.objects.get(username=username)
            projectObject = Projects.objects.get(projectname=projectname, projectUsers__contains=userObject.id)
            return {"result":"success", "data":"Specified user is member of project"}

        except db.DoesNotExist:
            return {"result":"failed", "data":"User not member of specified project"}

    def file(commandfile):
        try:
            fileDetails = Commands.objects.get(commandFile=commandfile)
            return {"result":"failed", "data":"file already exists"}

        except db.DoesNotExist:
            return {"result":"success", "data":"file does not exist"}



class Permissions:
    def create_user(username, email, role):
        if role not in ['Administrator', 'User', 'Privileged']:
            return {"result":"failed", "data":"Invalid Role selected for user"}

        try:
            userDetails = Users.objects.get(username=username)
            return {"result":"failed", "data":"User already exists"}

        except db.DoesNotExist:
            return {"result":"success", "data":"User does not exist"}

    def delete_user(username, ownuser):
        if username == ownuser:
            return {"result":"failed", "data":"Unable to remove self from database"}

        try:
            Users.objects.get(username=username)
            return {"result":"success", "data":"User exist"}

        except db.DoesNotExist:
            return {"result":"failed", "data":"Target user does not exist in the system"}

    def administrator(username):
        try:
            permissions = Users.objects(user=username, userRole="Administrator")
            return {"result":"success", "data":"User has sufficient rights to update projects"}

        except db.DoesNotExist:
            return {"result":"failed", "data":"Project does not exist or user does not have proper permissions"}


    def change_task(taskid, username):
        try:
            taskDetails = Tasks.objects.get(taskId=taskid)
            taskbeacon = taskDetails.beaconId
            beaconDetails = Beacons.objects.get(beaconId=taskbeacon)
            beaconTag = beaconDetails.beaconTag

            try:
                userDetails = ProjectUsers.objects.get(tag=beaconTag, user=username)

            except db.DoesNotExist:
                return {"result":"failed", "data":"User not authorized"}

            return {"result":"success", "data":"Task exists and user authorized"}

        except db.DoesNotExist:
            return {"result":"failed", "data":"Task does not exist"}

    def membership(username, projectname):
        try:
            userObject = Users.objects.get(username=username)
            projectObject = Projects.objects.get(projectname=projectname, projectUsers__contains=userObject.id)
            return {"result":"success", "data":"Specified user is member of project"}

        except db.DoesNotExist:
            return {"result":"failed", "data":"User not member of specified project"}
