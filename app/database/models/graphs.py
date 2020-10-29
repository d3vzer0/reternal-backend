from mongoengine import (Document, StringField, IntField,
    DateTimeField, EmbeddedDocumentField, EmbeddedDocumentListField,
    EmbeddedDocument, queryset_manager)
from datetime import datetime

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
