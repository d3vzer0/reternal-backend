
from pydantic import BaseModel, validator, Field
from typing import List, Dict
from datetime import datetime


class CreateActorReferencesIn(BaseModel):
    external_id: str = None
    url: str = None
    source_name: str = None
    description: str = None


class CreateActorTechniquesIn(BaseModel):
    technique_id: str
    name: str


class CreateActorIn(BaseModel):
    actor_id: str
    name: str
    description: str = None
    references: List[CreateActorReferencesIn]
    aliases: List[str] = None
    techniques: List[CreateActorTechniquesIn] = []


class CreateActorOut(BaseModel):
    id: str = Field(None, alias='_id')
    actor_id: str
    name: str
    description: str = None
    references: List[CreateActorReferencesIn]
    aliases: List[str] = None
    techniques: List[CreateActorTechniquesIn] = []
    
    @validator('id', pre=True, always=True)
    def _get_id(cls, v):
        return v['$oid']
