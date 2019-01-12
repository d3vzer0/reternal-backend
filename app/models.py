import datetime
import random, string
from app import db
from app.generic import Random

PLATFORMS = ('Windows', 'Linux', 'All', 'macOS')
STATUSOPTIONS = ('Processed', 'Open', 'Processing')
TYPEOPTIONS = ('Manual', 'Mitre', 'Actor')
ROLEOPTIONS = ('User', 'Admin')

class RevokedTokens(db.Document):
    token = db.StringField(max_length=100, required=True, unique=True)


class Users(db.Document):
    username = db.StringField(max_length=50, required=True, unique=True)
    password = db.StringField(max_length=128, required=True)
    salt = db.StringField(default=Random.create(20), max_length=20, required=True)
    role = db.StringField(max_length=20, required=True, default="User", choices=ROLEOPTIONS)
    email = db.EmailField(required=True)

    meta = {
        'ordering': ['-username'],
    }


class Macros(db.Document):
    command = db.StringField(max_length=100, required=True)
    input = db.StringField(max_length=900, required=False)
    name = db.StringField(max_length=40, required=True, unique=True)


class Credentials(db.Document):
    beacon_id = db.StringField(max_length=50, required=False)
    beacon_hostname = db.StringField(max_length=50, required=False)
    source_command = db.StringField(max_length=50, required=False)
    username = db.StringField(unique_with=['key', 'type'])
    key = db.StringField()
    type = db.StringField()


class Targets(db.Document):
    source_beacon = db.StringField(max_length=50, required=False)
    destination_ip = db.StringField(max_length=50)
    ports = db.DictField()
    hostname = db.StringField()


class Beacons(db.Document):
    beacon_id = db.StringField(max_length=150, required=True, unique=True)
    timestamp =  db.DateTimeField(default=datetime.datetime.now)
    platform = db.StringField(max_length=25, required=True)
    username = db.StringField(max_length=100, required=True)
    remote_ip = db.StringField(max_length=39, required=True)
    hostname = db.StringField(max_length=250, required=True)
    working_dir = db.StringField(max_length=800, required=False)
    timer = db.IntField(default=300)
    data = db.DictField()


class BeaconKeylogger(db.Document):
    beacon_id = db.StringField(max_length=150, required=True, unique=True)
    keyLoggerData = db.ListField()


class BeaconHistory(db.Document):
    beacon_id = db.StringField(max_length=150, required=True)
    platform = db.StringField(max_length=25, required=True)
    timestamp = db.DateTimeField(default=datetime.datetime.now)
    remote_ip = db.StringField(max_length=15, required=True)
    hostname = db.StringField(max_length=250, required=True)
    username = db.StringField(max_length=100, required=True)
    working_dir = db.StringField(max_length=400)
    timer = db.IntField()
    data = db.DictField()

    meta = {
        'ordering': ['-timestamp']
    }

class TaskCommands(db.EmbeddedDocument):
    reference = db.StringField(max_length=100, required=False, default=None)
    type = db.StringField(max_length=50, required=True, choices=TYPEOPTIONS)
    name = db.StringField(max_length=150, required=True)
    input = db.StringField(max_length=900, required=False)
    sleep = db.IntField(default=0)


class Recipes(db.Document):
    name = db.StringField(max_length=150, required=True, unique=True)
    commands = db.EmbeddedDocumentListField('TaskCommands', required=True)


class Tasks(db.Document):
    name = db.StringField(max_length=150, required=True)
    beacon_id = db.StringField(max_length=150, required=True)
    start_date = db.DateTimeField(default=datetime.datetime.now())
    task_status = db.StringField(default="Open", choices=STATUSOPTIONS)
    commands = db.EmbeddedDocumentListField('TaskCommands', required=True)
    meta = {
        'ordering': ['-start_date']
    }


class StartupTasks(db.Document):
    name = db.StringField(max_length=150, required=True, unique=True)
    platform = db.StringField(max_length=150, required=True)
    commands = db.EmbeddedDocumentListField('TaskCommands', required=True)


class TaskResults(db.Document):
    beacon_id = db.StringField(max_length=150, required=True)
    task_id = db.ReferenceField('Tasks', required=True)
    command = db.StringField(max_length=100, required=True) 
    type = db.StringField(max_length=50, required=True)
    input = db.StringField(max_length=900, required=True)
    end_date = db.DateTimeField(default=datetime.datetime.now)
    output = db.FileField()
    meta = {
        'ordering': ['-end_date'],
    }


class Commands(db.Document):
    name = db.StringField(max_length=100, required=True, unique=True)
    reference = db.StringField(max_length=100, required=False, default=None)
    type = db.StringField(max_length=20, required=True, choices=TYPEOPTIONS)
    platform = db.ListField(db.StringField(max_length=50, default="all"))


class CommandMapping(db.Document):
    author = db.StringField(max_length=100, required=False)
    name = db.StringField(max_length=100, required=True, unique_with=['technique_id', 'platform', 'kill_chain_phase'])
    description = db.StringField(max_length=200, required=False)
    reference = db.StringField(max_length=100, required=False, default=None)

    technique_id = db.StringField(max_length=200, required=True)
    technique_name = db.StringField(max_length=100, required=True)
    external_id = db.StringField(max_length=100, required=True)
    kill_chain_phase = db.StringField(max_length=100, required=True)
    platform = db.StringField(max_length=30, choices=PLATFORMS, required=True)
    commands = db.EmbeddedDocumentListField('TaskCommands', required=True)


class MitreReferences(db.EmbeddedDocument):
    external_id = db.StringField(max_length=100)
    url = db.StringField(max_length=1000)
    source_name = db.StringField(max_length=100)
    description = db.StringField(max_length=1000)


class Mitre(db.Document):
    references = db.EmbeddedDocumentListField('MitreReferences')
    platforms = db.ListField(db.StringField(max_length=50, default="all"))
    kill_chain_phases = db.ListField(db.StringField(max_length=100))
    permissions_required = db.ListField(db.StringField(max_length=100))
    technique_id = db.StringField(max_length=100, required=True, unique=True)
    name = db.StringField(max_length=100, required=True)
    description = db.StringField(max_length=9000)
    data_sources = db.ListField(db.StringField(max_length=100))
    detection = db.StringField(max_length=1000)

