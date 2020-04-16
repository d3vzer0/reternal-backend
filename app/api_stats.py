from app import api, celery
from app.utils.depends import validate_worker
from fastapi import Depends, Body
from app.database.models import Techniques, Coverage
from bson.json_util import dumps
from typing import List, Dict
import json


@api.get('/api/v1/stats/techniques')
async def stats_techniques():
    ''' Get the calculated score of the technique coverage '''
    unique_techniques = Techniques.objects().distinct('data_sources')
    matching_datasources = 'todo'
    return matching_datasources
