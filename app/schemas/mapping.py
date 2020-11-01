
from pydantic import BaseModel, validator, Field, root_validator
from typing import List, Dict, Optional
from app.database.models.techniques import Techniques
from app.schemas.attck import EmbeddedTechniquesOut
import json
import re

class TechniqueActorsOut(BaseModel):
    actor_id: str
    name: str

class TechniqueCommandsOut(BaseModel):
    category: str
    module: str
    integration: str
    input: Dict
    sleep: int


class MappingCountOut(BaseModel):
    id: str = Field(None, alias='_id')
    count: int


class MappingOut(BaseModel):
    id: str = Field(None, alias='_id')
    name: str
    author: str
    actors: Optional[List[TechniqueActorsOut]]
    commands: List[TechniqueCommandsOut]
    integration: str
    description: str
    external_id: str
    platform: str
    reference: str = None
    techniques: List[EmbeddedTechniquesOut]

    @validator('id', pre=True, always=True)
    def _get_id(cls, v):
        return v['$oid']

class MappingTechniquesOut(BaseModel):
    total: int
    results: List[MappingOut]

class MappingTechniquesIn(BaseModel):
    name: str
    reference: str
    external_id: str
    platform: str
    description: str = None
    reference: str = None
    author: str = None
    integration: str
    commands: List[TechniqueCommandsOut]
    techniques: Optional[List[EmbeddedTechniquesOut]]

    @root_validator(pre=True)
    def _get_techniques(cls, values):
        related_techniques =  [Techniques.objects(references__external_id=values['external_id'].upper()).first()]
        values['techniques'] = [json.loads(technique.to_json()) for technique in related_techniques if technique]
        return values