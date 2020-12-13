from mongoengine import (Document, StringField, IntField,
    EmbeddedDocument, EmbeddedDocumentField, EmbeddedDocumentListField,
    ListField, queryset_manager, BooleanField)
import json

PLATFORMS = ('Windows', 'Linux', 'All', 'macOS', 'AWS', 'Azure',
    'GCP', 'Office365', 'SaaS', 'Azure AD')


class EmbeddedCommandTechniques(EmbeddedDocument):
    platforms = ListField(StringField(max_length=50, default="all"))
    kill_chain_phases = ListField(StringField(max_length=100))
    permissions_required = ListField(StringField(max_length=100))
    technique_id = StringField(max_length=100, required=True)
    name = StringField(max_length=100, required=True)
    magma = EmbeddedDocumentField('Magma', required=False)
    data_sources = ListField(StringField(max_length=100))
    is_subtechnique =  BooleanField(default=False)
    meta = {'strict': False}

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
    actors = EmbeddedDocumentListField('EmbeddedTechniqueActors')
    techniques = EmbeddedDocumentListField(EmbeddedCommandTechniques)

    def to_dict(self):
        return json.loads(self.to_json())

    @queryset_manager
    def delete(doc_cls, queryset, mapping_id=None, *args, **kwargs):
        queryset.objects.get(id=mapping_id).delete()
        return {"message": "Successfully deleted mapping"}
