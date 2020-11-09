from mongoengine import (Document, StringField, IntField,
    ReferenceField, DateTimeField, DictField, EmbeddedDocument,
    EmbeddedDocumentListField, ListField)
from mongoengine.base.common import get_document as Model
import json
import re

PLATFORMS = ('Windows', 'Linux', 'All', 'macOS', 'AWS', 'Azure',
    'GCP', 'Office365', 'SaaS', 'Azure AD')

class SourceTypes(Document):
    integration = StringField(max_length=100)
    execution_date = DateTimeField()
    first_seen = DateTimeField()
    last_seen = DateTimeField()
    sourcetype = StringField(max_length=200, unique_with=['integration'])
    event_count = StringField(max_length=100)

    def create(*args, **kwargs):
        new_sourcetype = json.loads(SourceTypes.objects(sourcetype=kwargs['sourcetype']).upsert_one(**kwargs).to_json())
        return new_sourcetype


class Indices(Document):
    integration = StringField(max_length=100)
    execution_date = DateTimeField()
    index = StringField(max_length=100, unique_with=['integration', 'source', 'sourcetype'])
    source = StringField(max_length=800)
    sourcetype = StringField(max_length=200)
    event_count = StringField(max_length=100)

    def denormalize_coverage(indice, product):
        for datasource in product['datasources']:
            product_data = { 'name': product['name'],
                'platforms': product['platforms'],
                'sourcetype': indice['sourcetype'],
                'source': indice['source'],
                'vendor': product['vendor'],
                'index': indice['index']
            }
            get_coverage = Model('Coverage').objects(data_source_name=datasource).first()
            if not get_coverage:
                Model('Coverage').create(**{ 'enabled': True, 'data_source_name': datasource,
                    'products': [product_data]})
            else:
                get_coverage.update(add_to_set__products=product_data)

    def denormalize_products(indice):
        [Indices.denormalize_coverage(indice, product) for product in Products.objects() \
            if re.match(product['sourcetype'], indice['sourcetype'], re.IGNORECASE)]

    def create(*args, **kwargs):
        new_index = json.loads(Indices.objects(sourcetype=kwargs['sourcetype'], index=kwargs['index'],
            source=kwargs['source']).upsert_one(**kwargs).to_json())
        Indices.denormalize_products(kwargs)
        return new_index


class Products(Document):
    datasources = ListField(StringField(max_length=100))
    vendor = StringField(max_length=100)
    name = StringField(max_length=120)
    platforms = ListField(StringField(choices=PLATFORMS))
    sourcetype = StringField(max_length=100, unique=True)

    def create(*args, **kwargs):
        new_product = json.loads(Products.objects(sourcetype=kwargs['sourcetype']).upsert_one(**kwargs).to_json())
        return new_product

