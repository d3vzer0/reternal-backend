from app.database.models import Validations
from app import api, celery
from app.utils.depends import validate_worker
from fastapi import Depends, Body
from app.schemas.validations import ValidationsIn, ValidationsOut
from bson.json_util import dumps
from typing import List, Dict
import json


@api.post('/api/v1/validations', response_model=List[ValidationsOut])
async def create_validations(validation: ValidationsIn):
    create_validation = Validations.create(**validation.dict())
    return create_validation
