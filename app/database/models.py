from mongoengine import (connect, Document, StringField, IntField,
    ReferenceField, EmbeddedDocumentListField, ListField, EmbeddedDocument,
    DateTimeField, queryset_manager, EmbeddedDocumentField, UUIDField,
    BooleanField, DictField)
from mongoengine.errors import ValidationError, DoesNotExist, NotUniqueError, FieldDoesNotExist
from app.database.schemas import CampaignDenomIn
from app.environment import config
from datetime import datetime
import uuid, string, random, json, hashlib, re


# Init DB
connect(db='reternal', host=config['MONGO_HOST'],
    username=config['MONGO_USERNAME'], password=config['MONGO_PASSWORD'])

# Fixed options/choices for fields
PLATFORMS = ('Windows', 'Linux', 'All', 'macOS', 'AWS', 'Azure',
    'GCP', 'Office365', 'SaaS', 'Azure AD')
STATUSOPTIONS = ('Processed', 'Open', 'Processing')
SIGMASTATUSOPTIONS = ('stable', 'testing', 'experimental')


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
    start_date = DateTimeField(default=datetime.now())
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

    def denormalize_task(result):
        print('a')

    def result(result):
        get_module = ExecutedModules.objects(external_id=result['external_id'], 
            agent=result['agent'], end_date=None).update(
                set__end_date=result['end_date'], set__message=result['message']
            )
        ExecutedModules.denormalize_task(result)
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
    scheduled_date = DateTimeField(default=datetime.now())
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
    scheduled_date = DateTimeField(default=datetime.now())
    start_date = DateTimeField()
    end_date = DateTimeField()
    agents = EmbeddedDocumentListField('Agents', required=True)
    dependencies = ListField(StringField(max_length=100, required=True))
    state = StringField(max_length=100, required=False, choices=STATUSOPTIONS, default='Open')
    meta = {'strict': False}


class Campaigns(Document):
    name = StringField(max_length=100, required=True)
    group_id = StringField(required=True, unique=True)
    saved_date = DateTimeField(default=datetime.now())
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


class Magma(EmbeddedDocument):
    l1_usecase_name = StringField(max_length=120, required=True, default="Unclassified")
    l1_usecase_id = StringField(max_length=3, required=True, default="N/A")
    l2_usecase_name = StringField(max_length=120, required=True, default="Unclassified")
    l2_usecase_id = StringField(max_length=8, required=True, default="N/A")


class EmbeddedTechniques(EmbeddedDocument):
    references = EmbeddedDocumentListField('TechniqueReferences')
    platforms = ListField(StringField(max_length=50, default="all"))
    kill_chain_phases = ListField(StringField(max_length=100))
    permissions_required = ListField(StringField(max_length=100))
    technique_id = StringField(max_length=100, required=True)
    name = StringField(max_length=100, required=True)
    magma = EmbeddedDocumentField('Magma', required=False)
    description = StringField(max_length=9000)
    data_sources = ListField(StringField(max_length=100))
    data_sources_available = ListField(StringField(max_length=100), default=[])
    detection = StringField(max_length=1000)
    actors = EmbeddedDocumentListField('TechniqueActors')
    is_subtechnique =  BooleanField(default=False)
    meta = {'strict': False}


class Techniques(Document):
    references = EmbeddedDocumentListField('TechniqueReferences')
    platforms = ListField(StringField(max_length=50, default="all"))
    kill_chain_phases = ListField(StringField(max_length=100))
    permissions_required = ListField(StringField(max_length=100))
    technique_id = StringField(max_length=100, required=True, unique=True)
    name = StringField(max_length=100, required=True)
    magma = EmbeddedDocumentField('Magma', required=False)
    description = StringField(max_length=9000)
    data_sources = ListField(StringField(max_length=100))
    data_sources_available = ListField(StringField(max_length=100), default=[])
    detection = StringField(max_length=1000)
    actors = EmbeddedDocumentListField('TechniqueActors')
    is_subtechnique =  BooleanField(default=False)

    def update_sigma(**kwargs):
        get_techniques = Sigma.objects(techniques__technique_id__contains=kwargs['technique_id'])
        if get_techniques:
            updated_technique = SigmaTechniques(**kwargs)
            get_techniques.update_one(set__techniques__S=updated_technique)

    def update_commands(**kwargs):
        get_techniques = CommandMapping.objects(techniques__technique_id__contains=kwargs['technique_id'])
        if get_techniques: get_techniques.update_one(set__techniques__S=EmbeddedTechniques(**kwargs))

    def create(*args, **kwargs):
        new_technique = Techniques.objects(technique_id=kwargs['technique_id']).upsert_one(**kwargs)
        Techniques.update_sigma(**kwargs)
        return json.loads(new_technique.to_json())

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

# class Validations(Document):
#     author = StringField(max_length=100, required=False)
#     name = StringField(max_length=100, required=True, unique_with=['technique_id'])
#     description = StringField(max_length=200, required=False)
#     reference = StringField(max_length=100, required=False, default=None)
#     integration = StringField(max_length=100)
#     magma = EmbeddedDocumentField('Magma', required=False)
#     technique_id = StringField(max_length=200, required=True)
#     technique_name = StringField(max_length=100, required=True)
#     external_id = StringField(max_length=100, required=True)
#     kill_chain_phases = ListField(StringField(max_length=100, required=True))
#     search = StringField(max_length=2000)
#     coverage = DictField()
#     data_sources = ListField(StringField(max_length=100))
#     data_sources_available = ListField(StringField(max_length=100), default=[])
#     actors = EmbeddedDocumentListField('TechniqueActors')

#     def create(*args, **kwargs):
#         technique = Techniques.objects.get(references__external_id=kwargs['external_id'])
#         denomalized_technique = {**kwargs, 'technique_id': technique['technique_id'],
#             'technique_name': technique['name'], 'actors': technique['actors'],
#             'kill_chain_phases': technique['kill_chain_phases'], 'magma': technique['magma'],
#             'data_sources_available': technique['data_sources_available'] }

#         created_validations = json.loads(Validations.objects(name=kwargs['name']).upsert_one(**denomalized_technique).to_json())
#         return created_validations

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
    integration = StringField(max_length=100)
    technique_id = StringField(max_length=200, required=True)
    technique_name = StringField(max_length=100, required=True)
    external_id = StringField(max_length=100, required=True)
    kill_chain_phase = StringField(max_length=100, required=True)
    platform = StringField(max_length=30, choices=PLATFORMS, required=True)
    commands = EmbeddedDocumentListField('TaskCommands', required=True)
    actors = EmbeddedDocumentListField('TechniqueActors')
    techniques = EmbeddedDocumentListField(EmbeddedTechniques)


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
    sourcetype = StringField(max_length=200)
    source = StringField(max_length=800)
    index = StringField(max_length=100)
    platforms = ListField(StringField(choices=PLATFORMS))


class Coverage(Document):
    data_source_name = StringField(max_length=100, required=True, unique=True)
    date_registered = DateTimeField(default=datetime.now())
    date_connected = DateTimeField()
    available_for_data_analytics = BooleanField(default=False)
    enabled = BooleanField(default=True)
    products = EmbeddedDocumentListField('ProductConfiguration')
    comment = StringField()
    data_quality = EmbeddedDocumentField('DataQuality')

    def add_to_sigma(datasource):
        get_sigma_rules = Sigma.objects(techniques__data_sources__contains=datasource)
        get_sigma_rules.update_one(add_to_set__data_sources_available__S=datasource)
        return get_sigma_rules

    def pull_from_sigma(datasource):
        get_sigma_rules = Techniques.objects(data_sources_available__contains=datasource)
        get_sigma_rules.update(pull__data_sources_available__S=datasource)
        return get_sigma_rules

    def add_to_techniques(datasource):
        get_techniques = Techniques.objects(data_sources__contains=datasource)
        get_techniques.update(add_to_set__data_sources_available=datasource)
        return get_techniques

    def pull_from_techniques(coverage_name):
        get_techniques = Techniques.objects(data_sources_available__contains=coverage_name)
        get_techniques.update(pull__data_sources_available=coverage_name)
        return get_techniques

    # def add_to_validations(datasource):
    #     get_validations = Validations.objects(data_sources__contains=datasource)
    #     get_validations.update(add_to_set__data_sources_available=datasource)
    #     return get_validations

    # def pull_from_validations(coverage_name):
    #     get_validations = Validations.objects(data_sources_available__contains=coverage_name)
    #     get_validations.update(pull__data_sources_available=coverage_name)
    #     return get_validations

    def create(*args, **kwargs):
        new_mapping = Coverage.objects(data_source_name=kwargs['data_source_name']).upsert_one(**kwargs)
        Coverage.add_to_techniques(kwargs['data_source_name'])
        Coverage.add_to_validations(kwargs['data_source_name'])
        Coverage.add_to_sigma(kwargs['data_source_name'])
        return {"coverage_id": str(new_mapping.id)}

    def delete(coverage_id):
        cov_document = Coverage.objects.get(id=coverage_id)
        Coverage.pull_from_techniques(cov_document.data_source_name)
        Coverage.pull_from_validations(cov_document.data_source_name)
        Coverage.pull_from_sigma(cov_document.data_source_name)
        Coverage.objects(id=coverage_id).delete()
        return {"message": "Successfully deleted coverage_id"}


class SourceTypes(Document):
    integration = StringField(max_length=100)
    execution_date = DateTimeField()
    first_seen = DateTimeField()
    last_seen = DateTimeField()
    sourcetype = StringField(max_length=200, unique_with=['integration'])
    event_count = StringField(max_length=100)

    def create(*args, **kwargs):
        new_sourcetype = json.loads(SourceTypes.objects(sourcetype=kwargs['sourcetype']).upsert_one(**kwargs).to_json())
        return new_sourcetype


class Indices(Document):
    integration = StringField(max_length=100)
    execution_date = DateTimeField()
    index = StringField(max_length=100, unique_with=['integration', 'source', 'sourcetype'])
    source = StringField(max_length=800)
    sourcetype = StringField(max_length=200)
    event_count = StringField(max_length=100)

    def denormalize_coverage(indice, product):
        for datasource in product['datasources']:
            product_data = { 'name': product['name'],
                'platforms': product['platforms'],
                'sourcetype': indice['sourcetype'],
                'source': indice['source'],
                'vendor': product['vendor'],
                'index': indice['index']
            }
            get_coverage = Coverage.objects(data_source_name=datasource).first()
            if not get_coverage:
                Coverage.create(**{ 'enabled': True, 'data_source_name': datasource,
                    'products': [product_data]})
            else:
                get_coverage.update(add_to_set__products=product_data)

    def denormalize_products(indice):
        [Indices.denormalize_coverage(indice, product) for product in Products.objects() \
            if re.match(product['sourcetype'], indice['sourcetype'], re.IGNORECASE)]

    def create(*args, **kwargs):
        new_index = json.loads(Indices.objects(sourcetype=kwargs['sourcetype'], index=kwargs['index'],
            source=kwargs['source']).upsert_one(**kwargs).to_json())
        Indices.denormalize_products(kwargs)
        return new_index


class Products(Document):
    datasources = ListField(StringField(max_length=100))
    vendor = StringField(max_length=100)
    name = StringField(max_length=120)
    platforms = ListField(StringField(choices=PLATFORMS))
    sourcetype = StringField(max_length=100, unique=True)

    def create(*args, **kwargs):
        new_product = json.loads(Products.objects(sourcetype=kwargs['sourcetype']).upsert_one(**kwargs).to_json())
        return new_product


class SigmaTechniques(EmbeddedDocument):
    references = EmbeddedDocumentListField('TechniqueReferences')
    platforms = ListField(StringField(max_length=50, default="all"))
    kill_chain_phases = ListField(StringField(max_length=100))
    permissions_required = ListField(StringField(max_length=100))
    technique_id = StringField(max_length=100, required=True)
    name = StringField(max_length=100, required=True)
    magma = EmbeddedDocumentField('Magma', required=False)
    description = StringField(max_length=9000)
    data_sources = ListField(StringField(max_length=100))
    data_sources_available = ListField(StringField(max_length=100), default=[])
    detection = StringField(max_length=1000)
    actors = EmbeddedDocumentListField('TechniqueActors')
    is_subtechnique =  BooleanField(default=False)
    meta = {'strict': False}

class SigmaLogsource(EmbeddedDocument):
    category = StringField(required=False, max_length=400)
    product = StringField(required=False, max_length=400)
    service = StringField(required=False, max_length=400)
    definition = StringField(required=False, max_length=400)


class SigmaRelated(EmbeddedDocument):
    sigma_id = StringField(required=False, max_length=200)
    relation_type = StringField(required=False, choices=('derived', 'obsoletes', 'merged', 'renamed'))


class Sigma(Document):
    title = StringField(required=True, max_length=256)
    hash = StringField(required=True, max_length=256, unique=True)
    date = DateTimeField(required=False)
    description = StringField(required=False, max_length=900)
    author = StringField(required=False, max_length=255)
    references = ListField(StringField(max_length=500))
    status = StringField(required=False, choices=SIGMASTATUSOPTIONS)
    logsource = EmbeddedDocumentField(SigmaLogsource)
    detection = DictField()
    sigma_id = StringField(required=True, max_length=100)
    related = EmbeddedDocumentListField(SigmaRelated)
    license =  StringField(required=False, max_length=256)
    level = StringField(required=False, choices=('low', 'medium', 'high', 'critical'))
    tags = ListField(StringField(max_length=50, required=False))
    falsepositives = ListField(StringField(max_length=400, required=False))
    fields = ListField(StringField(max_length=100, required=True))
    techniques = EmbeddedDocumentListField(SigmaTechniques)

    def denormalize_attck(tags):
        related_techniques = [Techniques.objects(references__external_id=tag[-5:].upper()).first() for tag in tags 
            if re.match(r'attack\.t[0-9]{4}', tag)]
        return related_techniques

    def create(*args, **kwargs):
        kwargs['fields'] = kwargs.pop('sigma_fields', None)
        if 'tags' in kwargs:
            related_techniques =  Sigma.denormalize_attck(kwargs['tags'])
            kwargs['techniques'] = [json.loads(technique.to_json()) for technique in related_techniques if technique]
    
        sigma_hash = hashlib.sha256(str({'sigma_id': kwargs['sigma_id'], **kwargs['logsource'],
            **kwargs['detection']}).encode()).hexdigest()    
        new_rule = json.loads(Sigma.objects(hash=sigma_hash).upsert_one(**kwargs).to_json())
        return new_rule
