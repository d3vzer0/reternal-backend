from app import api, celery
from app.utils.depends import validate_worker
from app.schemas.user import User
from fastapi import Depends, Body
from database.models import Techniques, Coverage, Sigma
from bson.json_util import dumps
from typing import List, Dict
import json


@api.get('/api/v1/stats/count')
async def stats_count():
    ''' Get total count of mapped datasources '''
    stats_count = {
        'coverage': len(Coverage.objects(enabled=True)),
        'techniques': len(Techniques.objects()),
        'rules':  len(Sigma.objects())
    }
    return stats_count
