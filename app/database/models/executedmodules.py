from mongoengine import (Document, StringField, IntField,
    ReferenceField, DateTimeField, DictField)
from datetime import datetime


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
