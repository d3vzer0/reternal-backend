import requests
import json
from app.models import Mitre as MitreDB

url_techniques = "https://attack.mitre.org/api.php?action=ask&format=json&query=[[Category:Technique]]|?Has%20tactic|?Has%20ID|?Has%20display%20name|?Has%20platform|limit=9999"

class Mitre:
    def update_techniques(url):
        request_object = requests.get(url)
        json_object = request_object.json()
        for key, value in json_object['query']['results'].items():
            details = value['printouts']
            technique_id = details['Has ID'][0]
            technique_categories = details['Has tactic']
            technique_platforms = details['Has platform']
            technique_name = value['displaytitle']
            url = value['fullurl']
            for platform in technique_platforms:
                for category in technique_categories:
                    category_name = category['fulltext']
                    mitre_object = MitreDB(
                        platform=platform,
                        category=category_name,
                        technique_id=technique_id,
                        technique_name=technique_name,
                        url=url
                    ).save()

        return {'result':'success', 'message':'Done loading Mitre techniques'}

if __name__ == "__main__":
    Mitre.update_techniques(url_techniques)
