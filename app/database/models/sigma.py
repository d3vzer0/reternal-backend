from mongoengine import (Document, StringField, DictField,
    EmbeddedDocument, EmbeddedDocumentField, EmbeddedDocumentListField,
    ListField, DateTimeField, BooleanField, queryset_manager)
from mongoengine.base.common import get_document as Model
from mongoengine import signals
import json
import re

SIGMASTATUSOPTIONS = ('stable', 'testing', 'experimental')


class TechniqueReferences(EmbeddedDocument):
    external_id = StringField(max_length=100)
    url = StringField(max_length=1000)
    source_name = StringField(max_length=100)
    description = StringField(max_length=1000)


class EmbeddedSigmaActors(EmbeddedDocument):
    actor_id = StringField(max_length=100, required=False, unique=False)
    name = StringField(max_length=100, required=True)


class Magma(EmbeddedDocument):
    l1_usecase_name = StringField(max_length=120, required=True, default="Unclassified")
    l1_usecase_id = StringField(max_length=3, required=True, default="N/A")
    l2_usecase_name = StringField(max_length=120, required=True, default="Unclassified")
    l2_usecase_id = StringField(max_length=8, required=True, default="N/A")


class EmbeddedSigmaTechniques(EmbeddedDocument):
    meta = { 'strict': False }
    platforms = ListField(StringField(max_length=50, default="all"))
    kill_chain_phases = ListField(StringField(max_length=100))
    permissions_required = ListField(StringField(max_length=100))
    technique_id = StringField(max_length=100, required=True)
    name = StringField(max_length=100, required=True)
    magma = EmbeddedDocumentField('Magma', required=False)
    data_sources = ListField(StringField(max_length=100))
    is_subtechnique =  BooleanField(default=False)
    

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
    techniques = EmbeddedDocumentListField(EmbeddedSigmaTechniques)
    actors = EmbeddedDocumentListField(EmbeddedSigmaActors)
    data_sources = ListField(StringField(max_length=100))
    data_sources_available = ListField(StringField(max_length=100), default=[])

    def to_dict(self):
        return json.loads(self.to_json())
