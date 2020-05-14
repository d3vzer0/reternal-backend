from app import api, celery
from database.models import Tasks
from datetime import datetime, timedelta
from bson.json_util import dumps
from typing import List, Dict
import uuid
import json


async def get_task_next():
    ''' Calculate the next task to be executed, following the graph dependencies '''
    pipeline = [ {"$unwind": { "path": "$dependencies", "preserveNullAndEmptyArrays": True} },
        { "$lookup": {  "from": "tasks",  "as":"graph",  "let": { "dep": "$dependencies", "old": "$task", "camp": "$campaign"},
        "pipeline": [ { "$match": { "$expr": { "$and": [ { "$eq": [ "$task",  "$$dep" ] },{ "$eq": [ "$state", "Processed" ] },
        { "$eq": [ "$campaign", "$$camp" ] } ] } } } ]  } }, { "$match": { "$or":[{"graph": { "$ne": [] }}, {"dependencies": { "$exists": False }}] } } ]
    result = json.loads(dumps(Tasks.objects(start_date__lte=datetime.now()).aggregate(*pipeline)))
    return result
