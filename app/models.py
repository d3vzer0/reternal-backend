import datetime
import random, string
from app.functions_generic import Generic
from app import db


class StartupTasks(db.Document):
    command = db.ReferenceField('Commands')
    startup_id = db.StringField(max_length=24, required=True)
    input = db.StringField(max_length=150, required=False)
    platform = db.StringField(max_length=150, required=False)


class Macros(db.Document):
    command = db.ReferenceField('Commands')
    input = db.StringField(max_length=900, required=False)
    name = db.StringField(max_length=40, required=True, unique=True)


ROLE_OPTIONS = ('user', 'admin')
class Users(db.Document):
    username = db.StringField(max_length=50, required=True, unique=True)
    password = db.StringField(max_length=128, required=True)
    salt = db.StringField(default=Generic.create_random(20), max_length=20, required=True)

    role = db.StringField(max_length=20, required=True, default="User", choices=ROLE_OPTIONS)
    email = db.EmailField(required=True)

    meta = {
        'ordering': ['-username'],
    }

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
    platform = db.StringField(max_length=25, required=True)
    username = db.StringField(max_length=25, required=True)
    remote_ip = db.StringField(max_length=39, required=True)
    hostname = db.StringField(max_length=250, required=True)
    working_dir = db.StringField(max_length=400, required=False)
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


STATUSOPTIONS = ('Processed', 'Open', 'Processing')
class TaskCommands(db.EmbeddedDocument):
    type = db.StringField(max_length=50, required=True)
    name = db.StringField(max_length=150, required=True)
    input = db.StringField(max_length=900, required=False)
    sleep = db.IntField(default=0)


class Tasks(db.Document):
    beacon_id = db.StringField(max_length=150, required=True)
    start_date = db.DateTimeField(default=datetime.datetime.now())
    task_status = db.StringField(default="Open", choices=STATUSOPTIONS)
    commands = db.EmbeddedDocumentListField('TaskCommands', required=True)
    meta = {
        'ordering': ['-start_date']
    }


class TaskResults(db.Document):
    beacon_id = db.StringField(max_length=150, required=True)
    task_id = db.ReferenceField('Tasks', required=True)
    command = db.StringField(max_length=100, required=True) 
    type = db.StringField(max_length=50, required=True)
    input = db.StringField(max_length=900, required=True)
    end_date = db.DateTimeField(default=datetime.datetime.now)
    output = db.FileField()


class Commands(db.Document):
    name = db.StringField(max_length=100, required=True, unique=True)
    type = db.StringField(max_length=20, required=True)
    platform = db.ListField(db.StringField(max_length=50, default="all"))


class MitreCommands(db.Document):
    technique_id = db.StringField(max_length=100, required=True, unique=True)
    command = db.StringField(max_length=100, required=True)
    input = db.StringField(max_length=900, required=False)
    idle_time = db.IntField()
    metta_id = db.StringField(max_length=35)



class MitreReferences(db.EmbeddedDocument):
    external_id = db.StringField(max_length=100)
    url = db.StringField(max_length=1000)
    source_name = db.StringField(max_length=100)
    description = db.StringField(max_length=1000)


PLATFORMS = ('Windows', 'Linux', 'All', 'macOS')
class Mitre(db.Document):
    commands = db.EmbeddedDocumentListField('MitreCommands')
    references = db.EmbeddedDocumentListField('MitreReferences')
    platforms = db.ListField(db.StringField(max_length=50, default="all"))
    kill_chain_phases = db.ListField(db.StringField(max_length=100))
    permissions_required = db.ListField(db.StringField(max_length=100))
    technique_id = db.StringField(max_length=100, required=True, unique=True)
    name = db.StringField(max_length=100, required=True)
    description = db.StringField(max_length=9000)
    data_sources = db.ListField(db.StringField(max_length=100))
    detection = db.StringField(max_length=1000)


class RecipeTechniques(db.EmbeddedDocument):
    technique = db.ReferenceField('Mitre')
    idle_time = db.IntField()


class Recipe(db.Document):
    name = db.StringField(max_length=100)
    techniques = db.EmbeddedDocumentListField(RecipeTechniques)
