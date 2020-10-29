from mongoengine import (Document, StringField, IntField,
    ReferenceField, DateTimeField, DictField, EmbeddedDocument,
    EmbeddedDocumentListField, ListField)
from datetime import datetime
from app.database.models.agents import Agents

# Fixed options/choices for fields
STATUSOPTIONS = ('Processed', 'Scheduled', 'Processing')


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
    scheduled_date = DateTimeField()
    start_date = DateTimeField()
    end_date = DateTimeField()
    commands = EmbeddedDocumentListField('TaskCommands', required=True)
    sleep = IntField(default=0)
    agents = EmbeddedDocumentListField('Agents', required=True)
    state = StringField(max_length=100, required=False, choices=STATUSOPTIONS, default='Open')
    
    def create(schedule_data):
        new_schedule = Tasks(**schedule_data, scheduled_date=datetime.now()).save()
        return {"task": str(new_schedule.id)}
