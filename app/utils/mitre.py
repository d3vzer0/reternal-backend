from app.database.models import Actors, Techniques
import mongoengine
import requests
import json


class Mitre:
    def __init__(self, query_field):
        self.query_field = query_field

    def technique(self, reference_id):
        if self.query_field == 'id':
            mitre_object = Techniques.objects.get(technique_id=reference_id)
        elif self.query_field == 'external_id':
            mitre_object = Techniques.objects.get(references__external_id=reference_id)
        return {"result":"success", "data":mitre_object}

    def actor(self, reference_id):
        if self.query_field == 'id':
            actor_object = Actors.objects.get(actor_id=reference_id)
        elif self.query_field == 'external_id':
            actor_object = Actors.objects.get(references__external_id=reference_id)
        return {"result":"success", "data":actor_object}


class ImportMitre:
    def __init__(self, mitre_url='https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json'):
        self.mitre_url = mitre_url

    def technique(self, technique_details):
        killchain = [phase['phase_name'] for phase in technique_details['kill_chain_phases']]
        import_technique = Techniques.create(
            technique_id=technique_details['id'], name=technique_details['name'],
            description=technique_details['description'], platforms=technique_details['x_mitre_platforms'],
            permissions_required=technique_details.get('x_mitre_permissions_required', None),
            data_sources=technique_details.get('x_mitre_data_sources', None),
            references=technique_details['external_references'], kill_chain_phases=killchain)
        return import_technique

    def actor(self, technique_details):
        import_actor = Actors.create(actor_id=technique_details['id'], name=technique_details['name'],
            references=technique_details['external_references'],
            aliases= technique_details.get('aliases', None))
        return import_actor

    def relation(self, technique_details):
        for relation in technique_details:
            if 'intrusion-set' in relation['source_ref'] and 'attack-pattern' in relation['target_ref']:
                technique_object = Mitre('id').technique(relation['target_ref'])['data']
                actor_object = Mitre('id').actor(relation['source_ref'])['data']
                Techniques.relate(technique_object['technique_id'], actor_object['actor_id'], actor_object['name'])
                Actors.relate(actor_object['actor_id'], technique_object['technique_id'], technique_object['name'])
        return {'result':'success', 'message':'Finished loading relationships'}

    def update(self):
        relations = []
        request_object = requests.get(self.mitre_url)
        json_object = request_object.json()
        for technique_details in json_object['objects']:
            if technique_details['type'] == 'attack-pattern': self.technique(technique_details)
            elif technique_details['type'] == 'intrusion-set': self.actor(technique_details)
            elif technique_details['type'] == 'relationship': relations.append(technique_details)
        result = self.relation(relations)
        return result
