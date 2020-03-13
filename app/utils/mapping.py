from app.utils.mitre import Mitre
from app.database.models import CommandMapping
import glob
import os
import yaml

class FindFiles:
    def extension(path, ext):
        file_list = []
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in [f for f in filenames if f.endswith(ext)]:
                file_list.append(os.path.join(dirpath, filename))
        return file_list


class Mapping:
    def __init__(self, file_path='techniques', extension='.yml'):
        self.file_path = file_path
        self.extension = extension

    def update(self, name, technique_data, mapping_data, all_commands, phase):
        mitre_object = CommandMapping.create(
            name=name, technique_id=technique_data['technique_id'],
            technique_name=technique_data['name'], external_id=mapping_data['external_id'],
            kill_chain_phase=phase, platform=mapping_data['platform'], commands=all_commands,
            reference=mapping_data['reference'], actors=technique_data['actors'],
            author=mapping_data['author'], description=mapping_data['description'])
        return mitre_object

    def load(self):
        metta_files = FindFiles.extension(self.file_path, self.extension)
        for config_file in metta_files:
            with open(config_file) as yamlfile:
                yaml_object = yaml.load(yamlfile)
                try:
                    mapping_data = {
                        'name': yaml_object['name'],
                        'platform': yaml_object['mitre_technique']['platform'],
                        'reference': yaml_object.get('reference', None),
                        'description': yaml_object.get('description', None),
                        'author': yaml_object.get('author', None),
                        'technique': yaml_object['mitre_technique']['id'],
                        'commands': yaml_object['commands'],
                        'external_id': yaml_object['mitre_technique']['id']}

                    technique_object = Mitre('external_id').technique(mapping_data['external_id'])['data']
                    all_commands = [{"category":"Mitre", "module":command["module"], "input":command["input"],
                        "sleep":command["sleep"]} for command in mapping_data['commands']]

                    for phase in technique_object['kill_chain_phases']:
                        map_result = self.update(mapping_data['name'], technique_object, mapping_data, all_commands, phase)

                except Exception as err:
                    print(err)
                    pass

        return {'result':'success', 'message':'Finished loading mapped techniques'}

            


