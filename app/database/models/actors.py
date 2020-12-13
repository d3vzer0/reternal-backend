from mongoengine import (Document, StringField, IntField,
    EmbeddedDocument, EmbeddedDocumentField, EmbeddedDocumentListField,
    ListField, queryset_manager, BooleanField)
from mongoengine.base.common import get_document as Model
from app.schemas.techniques import TechniquesEmbeddedActorsOut
import json


class ActorReferences(EmbeddedDocument):
    url = StringField(max_length=300, required=False)
    description = StringField(max_length=1000, required=False)
    source_name = StringField(max_length=100, reuired=False)
    external_id = StringField(max_length=100, required=False)


class EmbeddedActorTechniques(EmbeddedDocument):
    platforms = ListField(StringField(max_length=50, default="all"))
    kill_chain_phases = ListField(StringField(max_length=100))
    permissions_required = ListField(StringField(max_length=100))
    technique_id = StringField(max_length=100, required=True)
    name = StringField(max_length=100, required=True)
    magma = EmbeddedDocumentField('Magma', required=False)
    data_sources = ListField(StringField(max_length=100))
    is_subtechnique =  BooleanField(default=False)


class Actors(Document):
    actor_id = StringField(max_length=100, required=True, unique=True)
    name = StringField(max_length=100, required=True)
    description = StringField(max_length=2000, required=False)
    references = EmbeddedDocumentListField('ActorReferences')
    aliases = ListField(StringField(max_length=100, required=False))
    techniques = EmbeddedDocumentListField('EmbeddedActorTechniques')

    def to_dict(self):
        return json.loads(self.to_json())

    def update_commands(self):
        get_related_commands = Model('CommandMapping').objects(actors__actor_id__contains=self.actor_id)
        if get_related_commands:
            embedded_actor = TechniquesEmbeddedActorsOut(**self.to_dict())
            get_related_commands.update(set__actors__S=Model('EmbeddedTechniqueActors')(**embedded_actor.dict()))

    def update_sigma(self):
        get_related_sigma = Model('Sigma').objects(actors__actor_id__contains=self.actor_id)
        if get_related_sigma:
            embedded_actor = TechniquesEmbeddedActorsOut(**self.to_dict())
            get_related_sigma.update(set__actors__S=Model('EmbeddedSigmaActors')(**embedded_actor.dict()))

    def update_techniques(self):
        get_related_techniques = Model('Techniques').objects(actors__actor_id__contains=self.actor_id)
        if get_related_techniques:
            embedded_actor = TechniquesEmbeddedActorsOut(**self.to_dict())
            get_related_techniques.update(set__actors__S=Model('EmbeddedTechniqueActors')(**embedded_actor.dict()))

    @queryset_manager
    def delete(doc_cls, queryset, actor_id=None, *args, **kwargs):
        queryset.objects.get(id=actor_id).delete()
        return {"message": "Successfully deleted actor"}


