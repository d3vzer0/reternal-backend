import datetime
from flask import url_for
from flask_login import UserMixin
import random, string
from app import db
import datetime


class StartupTasks(db.EmbeddedDocument):
    command = db.ReferenceField('Commands')
    startupId = db.StringField(max_length=24, required=True)
    taskInput = db.StringField(max_length=150, required=False)
    taskPlatform = db.StringField(max_length=150, required=False)


class Macros(db.EmbeddedDocument):
    command = db.ReferenceField('Commands')
    taskInput = db.StringField(max_length=900, required=False)
    macroIdentifier = db.StringField(max_length=40, required=True, unique=True)


class Users(db.Document):
    username = db.StringField(max_length=50, required=True, unique=True)
    password = db.StringField(max_length=128, required=True)
    saltGenerator = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(20))
    salt = db.StringField(default=saltGenerator, max_length=20, required=True)

    userRole = db.StringField(max_length=20, required=True, default="User")
    userEmail = db.EmailField(required=True)
    userDescription = db.StringField(default="Undefined", max_length=255, required=False)

    userProjects = db.ListField(db.ReferenceField('Projects'))
    userMacros = db.EmbeddedDocumentListField('Macros')
    userMessages = db.ListField(db.StringField(max_length='1000'))

    meta = {
        'ordering': ['-username'],
    }

    def clean(self):
        if self.username == "" or self.password == "" or self.userEmail == "":
            msg = "Unable to add empty username and/or password"
            raise ValidationError(msg)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username


class Credentials(db.Document):
    source_beacon = db.StringField(max_length=50, required=False)
    source_command = db.StringField(max_length=50, required=False)
    username = db.StringField(unique_with=['key', 'type'])
    key = db.StringField()
    type = db.StringField()


class Targets(db.Document):
    source_beacon = db.StringField(max_length=50, required=False)
    destination_ip = db.StringField(max_length=50)
    ports = db.DictField()
    hostname = db.StringField()


class Projects(db.Document):
    projectname = db.StringField(max_length=50, required=True, unique=True)
    projectDescription = db.StringField(default="Undefined", max_length=255, required=False)
    projectTag = db.StringField(max_length=100, required=False, unique=True)
    projectCreator = db.StringField(max_length=100, required=False)
    projectStartupTasks = db.EmbeddedDocumentListField('StartupTasks')
    projectUsers = db.ListField(db.ReferenceField('Users'))
    projectBeacons = db.ListField(db.ReferenceField('Beacons'))

    meta = {
        'ordering': ['-projectname'],
        'allow_inheritance':True,
    }

    def clean(self):
        if self.projectname == "":
            msg = "Unable to add empty projectname"
            raise ValidationError(msg)


class Beacons(db.Document):
    beaconId = db.StringField(max_length=150, required=True, unique=True)
    beaconTag = db.StringField(max_length=15, required=True)
    beaconProject = db.StringField(max_length=50, required=True)
    beaconPlatform = db.StringField(max_length=25, required=True)
    beaconTimer = db.IntField(default=300)
    beaconData = db.DictField()


class BeaconKeylogger(db.Document):
    beaconId = db.StringField(max_length=150, required=True, unique=True)
    keyLoggerData = db.ListField()


class BeaconHistory(db.Document):
    beaconId = db.StringField(max_length=150, required=True)
    beaconTimestamp = db.DateTimeField(default=datetime.datetime.now)
    beaconIp = db.StringField(max_length=15)
    beaconData = db.DictField()

    meta = {
        'ordering': ['-beaconTimestamp']
    }


STATUSOPTIONS = ('Processed', 'Open', 'Processing')
TASKTYPES = ('Single', 'Cron', 'Background')

class Tasks(db.Document):
    beaconId = db.StringField(max_length=150, required=True)
    taskId = db.StringField(max_length=10, required=True, unique=True)
    taskType = db.StringField(max_length=10, required=True, choices=TASKTYPES)
    taskOptions = db.StringField(max_length=100, required=False)
    taskCommandIdentifier = db.StringField(max_length=150, required=True)
    taskInput = db.StringField(max_length=900, required=False)
    taskStatus = db.StringField(max_length=10, required=True, choices=STATUSOPTIONS)
    taskStartdate = db.DateTimeField()

    meta = {
        'ordering': ['-taskStartdate']
    }


class TaskResults(db.Document):
    beaconId = db.StringField(max_length=150, required=True)
    taskId = db.StringField(max_length=10, required=True)
    taskEndDate = db.DateTimeField()
    taskOutput = db.FileField()


class Commands(db.Document):
    commandIdentifier = db.StringField(max_length=100, required=False, unique=True)
    commandFile = db.StringField(max_length=500, required=False, default="None")
    commandType = db.StringField(max_length=20, required=True)
    commandPlatform = db.ListField(db.StringField(max_length=50, default="all"))


class MitreCommands(db.EmbeddedDocument):
    command = db.ReferenceField('Commands')
    taskInput = db.StringField(max_length=900, required=False)


class Mitre(db.Document):
    commands = db.EmbeddedDocumentListField('MitreCommands')
    platform = db.StringField(max_length=50, default="all")
    category = db.StringField(max_length=100)
    technique_id = db.StringField(max_length=100, unique_with=['platform', 'category'])
    technique_name = db.StringField(max_length=100)
    url = db.StringField(max_length=1000)

# Cascade Delete rules
Projects.register_delete_rule(Users, 'userProjects', 4)
Users.register_delete_rule(Projects, 'projectUsers', 4)
