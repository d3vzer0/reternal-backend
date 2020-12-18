from py2neo import Graph
from py2neo.ogm import GraphObject, Property, RelatedFrom, RelatedTo
from neomodel import (config, StructuredNode, StringProperty, ArrayProperty,
    UniqueIdProperty, RelationshipTo)

# graph = Graph("bolt://neo4j:7687", auth=("neo4j", "neo5j"))
from neomodel import db
db.set_connection('bolt://neo4j:neo5j@neo4j:7687')

from neomodel import config
# before loading your node definitions
# config.AUTO_INSTALL_LABELS = True

class Reference(StructuredNode):
    external_id = StringProperty(unique_index=True)
    url = StringProperty()
    source_name = StringProperty()
    description = StringProperty()

class Technique(StructuredNode):
    references = RelationshipTo('Reference', 'REFERENCED_BY')
    platforms = ArrayProperty()
    kill_chain_phases =  ArrayProperty()
    permissions_required = ArrayProperty()
    technique_id = StringProperty(unique_index=True, required=True)
    name = StringProperty(required=True)
    description = StringProperty()
    data_sources = ArrayProperty()
    is_subtechnique = StringProperty()

# config.AUTO_INSTALL_LABELS = True