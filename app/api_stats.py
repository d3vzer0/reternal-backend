from app import api, celery
from app.utils.depends import validate_worker
from fastapi import Depends, Body
from app.database.models import Techniques, Coverage
from bson.json_util import dumps
from typing import List, Dict
import json


# @api.post('/api/v1/mitre/update')
# async def update_mitre():
#     update_db = ImportMitre().update()
#     return update_db
