from mongoengine import (connect, Document, StringField, IntField,
    ReferenceField, EmbeddedDocumentListField, ListField, EmbeddedDocument,
    DateTimeField, queryset_manager)
from app.environment import config
from app.utils.random import Random
import datetime
import pyotp
import json
import hashlib

# Fixed options/choices for fields
PLATFORMS = ('Windows', 'Linux', 'All', 'macOS')
STATUSOPTIONS = ('Processed', 'Open', 'Processing')

# Init DB
connect(db='reternal', host=config['MONGO_HOST'])

 # Database models
class TaskCommands(EmbeddedDocument):
    reference = ReferenceField('CommandMapping', required=False)
    reference_name = StringField(max_length=150, required=False)
    technique_name = StringField(max_length=150, required=False)
    kill_chain_phase = StringField(max_length=100)
    technique_id = StringField(max_length=100, required=False)
    type = StringField(max_length=50, required=True, choices=('Manual', 'Mitre', 'Actor'))
    name = StringField(max_length=150, required=True)
    input = StringField(max_length=900, required=False)
    sleep = IntField(default=0)


class Dependencies(EmbeddedDocument):
    source = StringField(max_length=100, required=True, db_field='from')
    destination = StringField(max_length=100, required=True)


class Tasks(EmbeddedDocument):
    name = StringField(max_length=100, required=True)
    commands = EmbeddedDocumentListField('TaskCommands', required=True)
    agents = ListField(StringField(max_length=100))
    sleep = IntField(default=0)
    start_date = DateTimeField(default=datetime.datetime.now())
    state = StringField(max_length=100, required=False, choices=STATUSOPTIONS, default='Open')
    agents = ListField(StringField(max_length=100), required=True)


class Campaigns(Document):
    name = StringField(max_length=100, required=True)
    tasks = EmbeddedDocumentListField('Tasks', required=True)
    dependencies = EmbeddedDocumentListField('Dependencies', required=False)

    @queryset_manager
    def get(doc_cls, queryset, campaign_id=None, *args, **kwargs):
        campaign_object = queryset.filter(id=campaign_id) if campaign_id else \
            queryset.only('id', 'name', 'tasks.name', 'tasks.start_date', 'tasks.state')
        result = json.loads(campaign_object.to_json())
        return result

    @queryset_manager
    def delete(doc_cls, queryset, campaign_id=None, *args, **kwargs):
        queryset.objects.get(id=campaign_id).delete()
        return {"message": "Successfully deleted campaign"}

    def create(campaign_data):
        new_campaign = Campaigns(**campaign_data).save()
        return {"campaign": str(new_campaign.id)}

class RevokedTokens(Document):
    token = StringField(max_length=100, required=True, unique=True)


class Users(Document):
    username = StringField(max_length=50, required=True, unique=True)
    password = StringField(max_length=128, required=True)
    salt = StringField(default=Random.create(20), max_length=20, required=True)
    role = StringField(max_length=20, required=True, default="User", choices=('User', 'Admin'))
    otp = StringField(max_length=16, required=False, default=pyotp.random_base32())

    meta = {
        'ordering': ['-username'],
    }
    
    @queryset_manager
    def delete(doc_cls, queryset, username, target_user, *args, **kwargs):
        if username == target_user:
            return {"result":"failed", "data":"Unable to remove self from database"}
        queryset.objects.get(username=target_user).delete()
        result = {'message':'Succesfully deleted user'}


    def create(username, password, role):
        salt = Random.create(20)
        password_hash = hashlib.sha512()
        password_string = salt + password
        password_hash.update(password_string.encode('utf-8'))
        password_hash = str(password_hash.hexdigest())
        new_user = Users(username=username, salt=salt, password=password_hash, role = role).save()
        return {'user': str(new_user.id)}


class Macros(Document):
    command = StringField(max_length=100, required=True)
    input = StringField(max_length=900, required=False)
    name = StringField(max_length=40, required=True, unique=True)

    @queryset_manager
    def delete(doc_cls, queryset, macro_id, *args, **kwargs):
        queryset.objects.get(id=macro_id).delete()
        return {"message": "Successfully deleted macro"}

    def create(macro_data):
        new_campaign = Macros(**macro_data).save()
        return {"campaign": str(new_campaign.id)}


class Recipes(Document):
    name = StringField(max_length=150, required=True, unique=True)
    commands = EmbeddedDocumentListField('TaskCommands', required=True)


class StartupTasks(Document):
    name = StringField(max_length=150, required=True, unique=True)
    platform = StringField(max_length=150, required=True)
    commands = EmbeddedDocumentListField('TaskCommands', required=True)


class TechniqueActors(EmbeddedDocument):
    actor_id = StringField(max_length=100, required=False, unique=False)
    name = StringField(max_length=100, required=True)


class TechniqueReferences(EmbeddedDocument):
    external_id = StringField(max_length=100)
    url = StringField(max_length=1000)
    source_name = StringField(max_length=100)
    description = StringField(max_length=1000)


class Techniques(Document):
    references = EmbeddedDocumentListField('TechniqueReferences')
    platforms = ListField(StringField(max_length=50, default="all"))
    kill_chain_phases = ListField(StringField(max_length=100))
    permissions_required = ListField(StringField(max_length=100))
    technique_id = StringField(max_length=100, required=True, unique=True)
    name = StringField(max_length=100, required=True)
    description = StringField(max_length=9000)
    data_sources = ListField(StringField(max_length=100))
    detection = StringField(max_length=1000)
    actors = EmbeddedDocumentListField('TechniqueActors')


class ActorReferences(EmbeddedDocument):
    url = StringField(max_length=300, required=False)
    description = StringField(max_length=1000, required=False)
    source_name = StringField(max_length=100, reuired=False)
    external_id = StringField(max_length=100, required=False)


class ActorTechniques(EmbeddedDocument):
    technique_id = StringField(max_length=100, required=False, unique=False)
    name = StringField(max_length=100, required=False)


class Actors(Document):
    actor_id = StringField(max_length=100, required=True, unique=True)
    name = StringField(max_length=100, required=True)
    description = StringField(max_length=2000, required=False)
    references = EmbeddedDocumentListField('ActorReferences')
    aliases = ListField(StringField(max_length=100, required=False))
    techniques = EmbeddedDocumentListField('ActorTechniques')


class CommandMapping(Document):
    author = StringField(max_length=100, required=False)
    name = StringField(max_length=100, required=True, unique_with=['technique_id', 'platform', 'kill_chain_phase'])
    description = StringField(max_length=200, required=False)
    reference = StringField(max_length=100, required=False, default=None)

    technique_id = StringField(max_length=200, required=True)
    technique_name = StringField(max_length=100, required=True)
    external_id = StringField(max_length=100, required=True)
    kill_chain_phase = StringField(max_length=100, required=True)
    platform = StringField(max_length=30, choices=PLATFORMS, required=True)
    commands = EmbeddedDocumentListField('TaskCommands', required=True)
    actors = EmbeddedDocumentListField('TechniqueActors')