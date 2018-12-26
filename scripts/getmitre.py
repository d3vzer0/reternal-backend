import requests
import json
from app.models import Mitre as MitreDB

url_techniques = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"

class Mitre:
    def update_techniques(url):
        request_object = requests.get(url)
        json_object = request_object.json()
        for technique_details in json_object['objects']:
            if technique_details['type'] == 'attack-pattern':

                # Single value
                technique_id = technique_details['id']
                name = technique_details['name']
                description = technique_details['description']

                # Unique lists
                platforms = technique_details['x_mitre_platforms']
                permissions_required = technique_details.get('x_mitre_permissions_required', None)
                data_sources = technique_details.get('x_mitre_data_sources', None)

                # List with key/value
                references = technique_details['external_references']
                killchain = []
                kill_chain_phases = technique_details['kill_chain_phases']
                for phase in kill_chain_phases:
                    killchain.append(phase['phase_name'])
                    
                try:
                    mitre_object = MitreDB(
                        name = name,
                        technique_id = technique_id,
                        description = description,
                        platforms = platforms,
                        permissions_required = permissions_required,
                        data_sources = data_sources,
                        references = references,
                        kill_chain_phases = killchain
                    ).save()

                except Exception as err:
                    print(err)
                    pass

        return {'result':'success', 'message':'Done loading Mitre techniques'}

if __name__ == "__main__":
    Mitre.update_techniques(url_techniques)


