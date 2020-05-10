from mongoengine import (connect, Document, StringField, IntField,
    ReferenceField, EmbeddedDocumentListField, ListField, EmbeddedDocument,
    DateTimeField, queryset_manager, EmbeddedDocumentField, UUIDField,
    BooleanField, DictField)
from app.environment import config
from app.utils.random import Random
from app.schemas.campaigns import CampaignDenomIn
import uuid
import datetime
import pyotp
import json
import hashlib

# Fixed options/choices for fields
PLATFORMS = ('Windows', 'Linux', 'All', 'macOS')
STATUSOPTIONS = ('Processed', 'Open', 'Processing')

# Init DB
connect(db='reternal', host=config['MONGO_HOST'])

class Agents(EmbeddedDocument):
    name = StringField(max_length=100, required=True)
    id = StringField(max_length=100, required=True)
    integration = StringField(max_length=100, required=True)


class ExecutedModules(Document):
    reference = ReferenceField('CommandMapping', required=False)
    reference_name = StringField(max_length=150, required=False)
    technique_name = StringField(max_length=150, required=False)
    kill_chain_phase = StringField(max_length=100)
    technique_id = StringField(max_length=100, required=False)
    category = StringField(max_length=50, required=True, choices=('Manual', 'Mitre', 'Actor'))
    module = StringField(max_length=150, required=True)
    integration = StringField(max_length=150, required=True)
    external_id = StringField(max_length=150, required=True)
    sleep = IntField(default=0)
    start_date = DateTimeField(default=datetime.datetime.now())
    end_date = DateTimeField()
    message = StringField(max_length=200)
    agent = StringField(max_length=100, required=True)
    task = StringField(max_length=100, required=True)
    group_id = StringField(max_length=100, unique_with=['task', 'module', 'agent', 'input'])
    campaign = StringField(max_length=100, required=True)
    input = DictField()

    def create(module_data):
        new_execution = ExecutedModules(**module_data).save()
        return {"executed_task": str(new_execution.id)}

    def result(result):
        get_module = ExecutedModules.objects(external_id=result['external_id'], 
            agent=result['agent'], integration=result['integration'], end_date=None).update(
                set__end_date=result['end_date'], set__message=result['message']
            )
        return {**result, 'response': get_module}

 # Database models
class TaskCommands(EmbeddedDocument):
    reference = ReferenceField('CommandMapping', required=False)
    reference_name = StringField(max_length=150, required=False)
    technique_name = StringField(max_length=150, required=False)
    kill_chain_phase = StringField(max_length=100)
    technique_id = StringField(max_length=100, required=False)
    category = StringField(max_length=50, required=True, choices=('Manual', 'Mitre', 'Actor'))
    module = StringField(max_length=150, required=True)
    integration = StringField(max_length=150, default='empire2')
    input = DictField()
    sleep = IntField(default=0)

class Dependencies(EmbeddedDocument):
    source = StringField(max_length=100, required=True, db_field='from')
    destination = StringField(max_length=100, required=True)


class Tasks(Document):
    task = StringField(max_length=100, required=True, unique_with='group_id')
    campaign = StringField(max_length=100, required=True)
    dependencies = ListField(StringField(max_length=100, required=True))
    group_id = StringField(required=True)
    scheduled_date = DateTimeField(default=datetime.datetime.now())
    start_date = DateTimeField()
    end_date = DateTimeField()
    commands = EmbeddedDocumentListField('TaskCommands', required=True)
    sleep = IntField(default=0)
    agents = EmbeddedDocumentListField('Agents', required=True)
    state = StringField(max_length=100, required=False, choices=STATUSOPTIONS, default='Open')
    
    def create(schedule_data):
        new_schedule = Tasks(**schedule_data).save()
        return {"task": str(new_schedule.id)}


class TaskData(EmbeddedDocument):
    name = StringField(max_length=100, required=True)
    commands = EmbeddedDocumentListField('TaskCommands', required=True)
    agents = ListField(StringField(max_length=100))
    sleep = IntField(default=0)
    agents = EmbeddedDocumentListField('Agents', required=True)


class CampaignTasks(EmbeddedDocument):
    name = StringField(max_length=100, required=True)
    scheduled_date = DateTimeField(default=datetime.datetime.now())
    start_date = DateTimeField()
    end_date = DateTimeField()
    agents = EmbeddedDocumentListField('Agents', required=True)
    dependencies = ListField(StringField(max_length=100, required=True))
    state = StringField(max_length=100, required=False, choices=STATUSOPTIONS, default='Open')
    meta = {'strict': False}

class Campaigns(Document):
    name = StringField(max_length=100, required=True)
    group_id = StringField(required=True, unique=True)
    saved_date = DateTimeField(default=datetime.datetime.now())
    tasks = EmbeddedDocumentListField('CampaignTasks', required=True)
    dependencies = EmbeddedDocumentListField('Dependencies')

    def denormalize_tasks(task, campaign_data, group_id):
        ''' Commit an individual task in the campaign graph '''
        task_content = { 'group_id':group_id, 'task': task['name'], 'campaign': campaign_data['name'],
            'commands': task['commands'], 'sleep': task['sleep'], 'agents': task['agents'],
            'state': 'Open', 'dependencies': [dep['source'] for dep in \
                campaign_data['dependencies'] if dep['destination'] == task['name']] }
        save_task = Tasks.create(task_content)
        return save_task

    def delete(group_id):
        get_campaign = Campaigns.objects(group_id=group_id).get()
        Campaigns.objects(group_id=group_id).delete()
        Tasks.objects(group_id=group_id).delete()
        return {'message': 'Succesfully deleted campaign'}

    def create(campaign_data):
        group_id = str(uuid.uuid4())
        campaign_tasks = [Campaigns.denormalize_tasks(task, campaign_data, group_id) for task in campaign_data['tasks']]
        denormalized_campaign = CampaignDenomIn(**campaign_data, group_id=group_id)
        new_campaign = Campaigns(**denormalized_campaign.dict()).save()
        return {'campaign': str(new_campaign.id), 'group_id': group_id, 'tasks': campaign_tasks}

class Edges(EmbeddedDocument):
    source = StringField(max_length=100, required=True, db_field='from')
    to = StringField(max_length=100, required=True)


class Nodes(EmbeddedDocument):
    id = StringField(max_length=100, required=True)
    label = StringField(max_length=100, required=True)
    taskData = EmbeddedDocumentField(TaskData)


class Graphs(Document):
    name = StringField(max_length=100, required=True, unique=True)
    nodes = EmbeddedDocumentListField(Nodes, required=True)
    edges = EmbeddedDocumentListField(Edges, required=False)

    def create(graph_data):
        new_graph = Graphs(**graph_data).save()
        return {"graph": str(new_graph.id)}

    @queryset_manager
    def delete(doc_cls, queryset, graph_id=None, *args, **kwargs):
        queryset.objects.get(id=graph_id).delete()
        return {"message": "Successfully deleted graph"}


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
    data_sources_available = ListField(StringField(max_length=100), default=[])
    detection = StringField(max_length=1000)
    actors = EmbeddedDocumentListField('TechniqueActors')
    
    def create(*args, **kwargs):
        new_technique = json.loads(Techniques.objects(technique_id=kwargs['technique_id']).upsert_one(**kwargs).to_json())
        return new_technique

    @queryset_manager
    def delete(doc_cls, queryset, technique_id=None, *args, **kwargs):
        queryset.objects.get(id=technique_id).delete()
        return {"message": "Successfully deleted technique"}

    def relate(technique_id, actor_id, name, *args, **kwargs):
        technique_object = Techniques.objects.get(technique_id=technique_id)
        technique_actors = TechniqueActors(actor_id=actor_id, name=name)
        append_actors = technique_object.actors.append(technique_actors)
        technique_object.save()
        return {'message':'Succesfully added technique relationship'}



class Validations(Document):
    author = StringField(max_length=100, required=False)
    name = StringField(max_length=100, required=True, unique_with=['technique_id', 'kill_chain_phase'])
    description = StringField(max_length=200, required=False)
    reference = StringField(max_length=100, required=False, default=None)
    integration = StringField(max_length=100)
    technique_id = StringField(max_length=200, required=True)
    technique_name = StringField(max_length=100, required=True)
    external_id = StringField(max_length=100, required=True)
    kill_chain_phase = StringField(max_length=100, required=True)
    queries = ListField(StringField(max_length=2000))
    data_sources = ListField(StringField(max_length=100))
    actors = EmbeddedDocumentListField('TechniqueActors')

    def create(*args, **kwargs):
        technique = Techniques.objects.get(references__external_id=kwargs['external_id'])
        created_validations = []
        for phase in technique['kill_chain_phases']:
            leRes = {**kwargs, 'technique_id': technique['technique_id'],
                'technique_name': technique['name'], 'actors': technique['actors'],
                'kill_chain_phase': phase }
            new_mapping = Validations.objects(name=kwargs['name']).upsert_one(**leRes)
            created_validations.append(json.loads(new_mapping.to_json()))
        return created_validations

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

    def create(*args, **kwargs):
        new_actor = json.loads(Actors.objects(actor_id=kwargs['actor_id']).upsert_one(**kwargs).to_json())
        return new_actor

    @queryset_manager
    def delete(doc_cls, queryset, actor_id=None, *args, **kwargs):
        queryset.objects.get(id=actor_id).delete()
        return {"message": "Successfully deleted actor"}

    def relate(actor_id, technique_id, name, *args, **kwargs):
        actor_object = Actors.objects.get(actor_id=actor_id)
        actor_techniques = ActorTechniques(technique_id=technique_id, name=name )
        actor_object.techniques.append(actor_techniques)
        actor_object.save()
        return {'message':'Succesfully added actor relationship'}

class CommandMapping(Document):
    author = StringField(max_length=100, required=False)
    name = StringField(max_length=100, required=True, unique_with=['technique_id', 'platform', 'kill_chain_phase'])
    description = StringField(max_length=200, required=False)
    reference = StringField(max_length=100, required=False, default=None)
    integrations = ListField(StringField(max_length=100))
    technique_id = StringField(max_length=200, required=True)
    technique_name = StringField(max_length=100, required=True)
    external_id = StringField(max_length=100, required=True)
    kill_chain_phase = StringField(max_length=100, required=True)
    platform = StringField(max_length=30, choices=PLATFORMS, required=True)
    commands = EmbeddedDocumentListField('TaskCommands', required=True)
    actors = EmbeddedDocumentListField('TechniqueActors')


    def create(*args, **kwargs):
        technique = Techniques.objects.get(references__external_id=kwargs['external_id'])
        created_mappings = []
        for phase in technique['kill_chain_phases']:
            leRes = {**kwargs, 'technique_id': technique['technique_id'],
                'technique_name': technique['name'], 'actors': technique['actors'],
                'kill_chain_phase': phase }
            new_mapping = CommandMapping.objects(name=kwargs['name']).upsert_one(**leRes)
            created_mappings.append(json.loads(new_mapping.to_json()))
        return created_mappings

    @queryset_manager
    def delete(doc_cls, queryset, mapping_id=None, *args, **kwargs):
        queryset.objects.get(id=mapping_id).delete()
        return {"message": "Successfully deleted mapping"}


class DataQuality(EmbeddedDocument):
    device_completeness = IntField(min_value=0, max_value=5, default=0)
    field_completeness = IntField(min_value=0, max_value=5, default=0)
    timeliness = IntField(min_value=0, max_value=5, default=0)
    consistency = IntField(min_value=0, max_value=5, default=0)
    retention = IntField(min_value=0, max_value=5, default=0)


class ProductConfiguration(EmbeddedDocument):
    name = StringField(max_length=120)
    vendor = StringField(max_length=100)
    sourcetype = StringField(max_length=30)
    source = StringField(max_length=30)
    index = StringField(max_length=30)

class Coverage(Document):
    data_source_name = StringField(max_length=100, required=True, unique=True)
    date_registered = DateTimeField(default=datetime.datetime.now())
    date_connected = DateTimeField()
    available_for_data_analytics = BooleanField(default=False)
    enabled = BooleanField(default=False)
    products = EmbeddedDocumentListField('ProductConfiguration')
    comment = StringField()
    data_quality = EmbeddedDocumentField('DataQuality')

    def add_to_techniques(datasource):
        get_techniques = Techniques.objects(data_sources__contains=datasource)
        get_techniques.update(add_to_set__data_sources_available=datasource)
        return get_techniques

    def pull_from_techniques(coverage_name):
        get_techniques = Techniques.objects(data_sources_available__contains=coverage_name)
        get_techniques.update(pull__data_sources_available=coverage_name)
        return get_techniques

    def create(*args, **kwargs):
        new_mapping = Coverage.objects(data_source_name=kwargs['data_source_name']).upsert_one(**kwargs)
        Coverage.add_to_techniques(kwargs['data_source_name'])
        return {"coverage_id": str(new_mapping.id)}

    def delete(coverage_id):
        cov_document = Coverage.objects.get(id=coverage_id)
        Coverage.pull_from_techniques(cov_document.data_source_name)
        Coverage.objects(id=coverage_id).delete()
        return {"message": "Successfully deleted coverage_id"}
