from mongoengine import (Document, StringField, IntField,
    DateTimeField, EmbeddedDocumentField, EmbeddedDocumentListField,
    EmbeddedDocument, queryset_manager)
from datetime import datetime


class Recipes(Document):
    name = StringField(max_length=150, required=True, unique=True)
    commands = EmbeddedDocumentListField('TaskCommands', required=True)
