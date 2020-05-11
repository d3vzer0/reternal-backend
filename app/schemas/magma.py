
from pydantic import BaseModel, validator, Field
from typing import List, Dict
from datetime import datetime

class CreateMagmaIn(BaseModel):
    l1_usecase_name: str
    l1_usecase_id: str
    l2_usecase_name: str
    l2_usecase_id: str
    external_id: str

class CreateMagmaOut(BaseModel):
    id: str = Field(None, alias='_id')
    l1_usecase_name: str
    l1_usecase_id: str
    l2_usecase_name: str
    l2_usecase_id: str
    external_id: str

    @validator('id', pre=True, always=True)
    def _get_id(cls, v):
        return v['$oid']

