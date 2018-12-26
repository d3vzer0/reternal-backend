import glob
import os
import yaml
from app.models import Mitre, MitreCommands

exec_id = '5b8f9785d6c66c3dd35ab36b'

class MettaParser:
    def find_files(path):
        file_list = []
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in [f for f in filenames if f.endswith(".yml")]:
                file_list.append(os.path.join(dirpath, filename))
        return file_list

    def parse_file(filepath):
        with open(filepath) as yamlfile:
            yaml_object = yaml.load(yamlfile)
            try:
                platform = yaml_object['os']
                category = yaml_object['meta']['mitre_attack_phase']
                technique = yaml_object['meta']['mitre_attack_technique']
                commands = yaml_object['meta']['purple_actions']
                platform_mapping = {
                    "windows":"Windows",
                    "linux":"Linux",
                    "osx":"macOS"
                }

                mitre_object =  Mitre.objects.get(platform=platform_mapping[platform],
                    technique_name=technique, category=category)

                for key, value in commands.items():
                    hue = value.replace('cmd.exe /c', '').strip()
                    task_object = MitreCommands(command=exec_id, taskInput=hue)
                    mitre_object.commands.append(task_object)
                    mitre_object.save()


            except Exception as err:
                print(err)


if __name__ == "__main__":
    config_files = MettaParser.find_files('MITRE')
    for config_file in config_files:
        parse_config = MettaParser.parse_file(config_file)
