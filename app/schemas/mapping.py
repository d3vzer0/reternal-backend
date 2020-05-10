
from pydantic import BaseModel, validator, Field
from typing import List, Dict
from datetime import datetime

class TechniqueActorsOut(BaseModel):
    actor_id: str
    name: str

class TechniqueCommandsOut(BaseModel):
    category: str
    module: str
    input: Dict
    sleep: int


class MappingCountOut(BaseModel):
    id: str = Field(None, alias='_id')
    count: int


class MappingTechniquesOut(BaseModel):
    id: str = Field(None, alias='_id')
    name: str
    author: str
    actors: List[TechniqueActorsOut]
    commands: List[TechniqueCommandsOut]
    integrations: List[str]
    description: str
    external_id: str
    kill_chain_phase: str
    platform: str
    reference: str = None
    technique_id: str
    technique_name: str

    @validator('id', pre=True, always=True)
    def _get_id(cls, v):
        return v['$oid']


class MappingTechniquesIn(BaseModel):
    name: str
    reference: str
    external_id: str
    platform: str
    description: str = None
    author: str = None
    integrations: List[str] = ['generic']
    commands: List[TechniqueCommandsOut]
