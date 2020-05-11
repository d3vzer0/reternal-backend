
from pydantic import BaseModel, validator, Field
from typing import List, Dict
from datetime import datetime

class ValidationActorsOut(BaseModel):
    actor_id: str
    name: str

class ValidationsMagmaOut(BaseModel):
    l1_usecase_name: str
    l1_usecase_id: str
    l2_usecase_name: str
    l2_usecase_id: str

class ValidationsOut(BaseModel):
    id: str = Field(None, alias='_id')
    name: str
    author: str
    actors: List[ValidationActorsOut]
    search: str
    magma: ValidationsMagmaOut = None
    integration: str
    description: str
    coverage: Dict
    external_id: str
    kill_chain_phases: List[str]
    data_sources: List[str]
    data_sources_available: List[str]
    reference: str = None
    technique_id: str
    technique_name: str
    reference: str = None

    @validator('id', pre=True, always=True)
    def _get_id(cls, v):
        return v['$oid']


class ValidationsIn(BaseModel):
    name: str
    external_id: str
    data_sources: List[str]
    coverage: Dict
    reference: str = None
    description: str = None
    author: str = None
    integration: str
    search: str
