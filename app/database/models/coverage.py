from mongoengine import (Document, StringField, IntField,
    EmbeddedDocument, EmbeddedDocumentField, EmbeddedDocumentListField,
    ListField, DateTimeField, BooleanField)
from mongoengine.base.common import get_document as Model
from datetime import datetime
import json

PLATFORMS = ('Windows', 'Linux', 'All', 'macOS', 'AWS', 'Azure',
    'GCP', 'Office365', 'SaaS', 'Azure AD')

class DataQuality(EmbeddedDocument):
    device_completeness = IntField(min_value=0, max_value=5, default=0)
    field_completeness = IntField(min_value=0, max_value=5, default=0)
    delay = IntField(min_value=0, max_value=5, default=0)
    consistency = IntField(min_value=0, max_value=5, default=0)
    retention = IntField(min_value=0, max_value=5, default=0)


class ProductConfiguration(EmbeddedDocument):
    name = StringField(max_length=120)
    vendor = StringField(max_length=100)
    sourcetype = StringField(max_length=200)
    source = StringField(max_length=800)
    index = StringField(max_length=100)
    platforms = ListField(StringField(choices=PLATFORMS))
    fields = ListField(StringField(max_length=100))


class Coverage(Document):
    data_source_name = StringField(max_length=100, required=True, unique=True)
    date_registered = DateTimeField()
    date_connected = DateTimeField()
    available_for_data_analytics = BooleanField(default=False)
    enabled = BooleanField(default=True)
    products = EmbeddedDocumentListField('ProductConfiguration')
    comment = StringField()
    data_quality = EmbeddedDocumentField('DataQuality')

    def add_to_sigma(datasource):
        get_sigma_rules = Model('Sigma').objects(data_sources__contains=datasource)
        get_sigma_rules.update_one(add_to_set__data_sources_available__S=datasource)
        return get_sigma_rules

    def pull_from_sigma(datasource):
        get_sigma_rules = Model('Techniques').objects(data_sources_available__contains=datasource)
        get_sigma_rules.update(pull__data_sources_available__S=datasource)
        return get_sigma_rules

    def add_to_techniques(datasource):
        get_techniques = Model('Techniques').objects(data_sources__contains=datasource)
        get_techniques.update(add_to_set__data_sources_available=datasource)
        return get_techniques

    def pull_from_techniques(coverage_name):
        get_techniques = Model('Techniques').objects(data_sources_available__contains=coverage_name)
        get_techniques.update(pull__data_sources_available=coverage_name)
        return get_techniques

    # def add_to_validations(datasource):
    #     get_validations = Validations.objects(data_sources__contains=datasource)
    #     get_validations.update(add_to_set__data_sources_available=datasource)
    #     return get_validations

    # def pull_from_validations(coverage_name):
    #     get_validations = Validations.objects(data_sources_available__contains=coverage_name)
    #     get_validations.update(pull__data_sources_available=coverage_name)
    #     return get_validations

    def create(*args, **kwargs):
        new_mapping = Coverage.objects(data_source_name=kwargs['data_source_name']).upsert_one(**kwargs,
            date_registered=datetime.now())
        Coverage.add_to_techniques(kwargs['data_source_name'])
        Coverage.add_to_sigma(kwargs['data_source_name'])
        return {"coverage_id": str(new_mapping.id)}

    def delete(coverage_id):
        cov_document = Coverage.objects.get(id=coverage_id)
        Coverage.pull_from_techniques(cov_document.data_source_name)
        # Coverage.pull_from_validations(cov_document.data_source_name)
        Coverage.pull_from_sigma(cov_document.data_source_name)
        Coverage.objects(id=coverage_id).delete()
        return {"message": "Successfully deleted coverage_id"}

