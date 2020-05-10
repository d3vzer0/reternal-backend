
from pydantic import BaseModel, validator, Field
from typing import List, Dict
from datetime import datetime

class ValidationActorsOut(BaseModel):
    actor_id: str
    name: str


class ValidationsOut(BaseModel):
    id: str = Field(None, alias='_id')
    name: str
    author: str
    actors: List[ValidationActorsOut]
    queries: List[str]
    integration: str
    description: str
    external_id: str
    kill_chain_phase: str
    reference: str = None
    technique_id: str
    technique_name: str

    @validator('id', pre=True, always=True)
    def _get_id(cls, v):
        return v['$oid']


class ValidationsIn(BaseModel):
    name: str
    external_id: str
    description: str = None
    author: str = None
    integration: str
    queries: List[str]
