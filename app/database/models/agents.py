from mongoengine import (connect, Document, StringField, IntField,
    ReferenceField, EmbeddedDocumentListField, ListField, EmbeddedDocument,
    DateTimeField, queryset_manager, EmbeddedDocumentField, UUIDField,
    BooleanField, DictField, MapField)
from mongoengine.errors import ValidationError, DoesNotExist, NotUniqueError, FieldDoesNotExist
from app.database.schemas import CampaignDenomIn
from app.environment import config
from datetime import datetime
import uuid, string, random, json, hashlib, re


class Agents(EmbeddedDocument):
    name = StringField(max_length=100, required=True)
    id = StringField(max_length=100, required=True)
    integration = StringField(max_length=100, required=True)
