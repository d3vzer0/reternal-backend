from mongoengine import (Document, StringField, IntField,
    EmbeddedDocument, EmbeddedDocumentField, EmbeddedDocumentListField,
    ListField, queryset_manager, BooleanField, DateTimeField, DictField)
from mongoengine.base.common import get_document as Model
from app.schemas.attck import EmbeddedTechniquesOut, EmbeddedActorTechniquesOut
from mongoengine.queryset import QuerySet
import json


SIGMASTATUSOPTIONS = ('stable', 'testing', 'experimental')


class TechniqueReferences(EmbeddedDocument):
    external_id = StringField(max_length=100)
    url = StringField(max_length=1000)
    source_name = StringField(max_length=100)
    description = StringField(max_length=1000)


class EmbeddedTechniqueActors(EmbeddedDocument):
    actor_id = StringField(max_length=100, required=False, unique=False)
    name = StringField(max_length=100, required=True)


class Magma(EmbeddedDocument):
    l1_usecase_name = StringField(max_length=120, required=True, default="Unclassified")
    l1_usecase_id = StringField(max_length=3, required=True, default="N/A")
    l2_usecase_name = StringField(max_length=120, required=True, default="Unclassified")
    l2_usecase_id = StringField(max_length=8, required=True, default="N/A")


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
    actors = EmbeddedDocumentListField('EmbeddedTechniqueActors')
    is_subtechnique =  BooleanField(default=False)
    meta = {
      'strict': False
    }


class CustomQuerySet(QuerySet):
    # def update_sigma(self):
    #     for doc in self:
    #         get_related_sigma = Model('Sigma').objects(techniques__technique_id__contains=doc.technique_id)
    #         if get_related_sigma:
    #             embedded_technique = EmbeddedTechniquesOut(**doc.to_dict())
    #             get_related_sigma.update(set__techniques__S=Model('EmbeddedSigmaTechniques')(**embedded_technique.dict()))

    def update_commands(self):
        for doc in self:
            get_techniques = Model('CommandMapping').objects(techniques__technique_id__contains=doc.technique_id)
            if get_techniques:
                embedded_technique = EmbeddedTechniquesOut(**doc.to_dict())
                get_techniques.update(set__techniques__S=Model('EmbeddedCommandTechniques')(**embedded_technique.dict()))

    def update_actors(self):
        for doc in self:
            get_techniques = Model('Actors').objects(techniques__technique_id__contains=doc.technique_id)
            if get_techniques:
                embedded_technique = EmbeddedActorTechniquesOut(**doc.to_dict())
                get_techniques.update(set__techniques__S=Model('EmbeddedActorTechniques')(**embedded_technique.dict()))


class Techniques(Document):
    # meta = {'queryset_class': CustomQuerySet}
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
    actors = EmbeddedDocumentListField('EmbeddedTechniqueActors')
    is_subtechnique = BooleanField(default=False)

    def to_dict(self):
        return json.loads(self.to_json())

    def update_sigma(self):
        get_related_sigma = Model('Sigma').objects(techniques__technique_id__contains=self.technique_id)
        if get_related_sigma:
            print(get_related_sigma)
            embedded_technique = EmbeddedTechniquesOut(**self.to_dict())
            get_related_sigma.update(set__techniques__S=Model('EmbeddedSigmaTechniques')(**embedded_technique.dict()))


    @queryset_manager
    def delete(doc_cls, queryset, technique_id=None, *args, **kwargs):
        queryset.objects.get(id=technique_id).delete()
        return {"message": "Successfully deleted technique"}

