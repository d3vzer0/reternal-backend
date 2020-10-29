from mongoengine import (Document, StringField, IntField,
    DateTimeField, EmbeddedDocumentField, EmbeddedDocumentListField,
    ListField, EmbeddedDocument)
from datetime import datetime
import json

STATUSOPTIONS = ('Processed', 'Scheduled', 'Processing')


class Edges(EmbeddedDocument):
    source = StringField(max_length=100, required=True)
    destination = StringField(max_length=100, required=True)


class Nodes(EmbeddedDocument):
    name = StringField(max_length=100, required=True)
    commands = EmbeddedDocumentListField('TaskCommands', required=True)
    sleep = IntField(default=0)
    agent = EmbeddedDocumentField('Agents', required=True)
    state = StringField(default='Scheduled', choices=STATUSOPTIONS)
    scheduled_date = DateTimeField()
    start_date = DateTimeField()
    end_date = DateTimeField()


class Campaigns(Document):
    name = StringField(max_length=100, required=True)
    state = StringField(default='Scheduled', choices=STATUSOPTIONS)
    nodes = EmbeddedDocumentListField('Nodes', required=True)
    edges = EmbeddedDocumentListField('Edges')
    saved_date =  DateTimeField()

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
        new_campaign = Campaigns(**campaign_data, saved_date=datetime.now()).save()
        return json.loads(new_campaign.to_json())


class CampaignTasks(EmbeddedDocument):
    name = StringField(max_length=100, required=True)
    scheduled_date = DateTimeField(default=datetime.now())
    start_date = DateTimeField()
    end_date = DateTimeField()
    agents = EmbeddedDocumentListField('Agents', required=True)
    dependencies = ListField(StringField(max_length=100, required=True))
    state = StringField(max_length=100, required=False, choices=STATUSOPTIONS, default='Open')
    meta = {'strict': False}


class CampaignTasks(EmbeddedDocument):
    name = StringField(max_length=100, required=True)
    scheduled_date = DateTimeField(default=datetime.now())
    start_date = DateTimeField()
    end_date = DateTimeField()
    agents = EmbeddedDocumentListField('Agents', required=True)
    dependencies = ListField(StringField(max_length=100, required=True))
    state = StringField(max_length=100, required=False, choices=STATUSOPTIONS, default='Open')
    meta = {'strict': False}