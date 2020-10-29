
from pydantic import BaseModel, validator, Field
from typing import List, Dict
from datetime import datetime


class TechniquesEmbeddedActorsOut(BaseModel):
    actor_id: str
    name: str


class CreateTechniquesReferencesIn(BaseModel):
    external_id: str = None
    url: str = None
    source_name: str = None
    description: str = None


class CreateTechniquesActorsIn(BaseModel):
    actor_id: str
    name: str

class CreateTechniquesMagmaIn(BaseModel):
    l1_usecase_name: str
    l1_usecase_id: str
    l2_usecase_name: str
    l2_usecase_id: str


class CreateTechniquesIn(BaseModel):
    references: List[CreateTechniquesReferencesIn]
    platforms: List[str]
    kill_chain_phases: List[str]
    permissions_required: List[str]
    technique_id: str
    magma: CreateTechniquesMagmaIn = None
    name: str
    description: str = None
    data_sources: List[str]
    data_sources_available: List[str] = []
    detection: str = None
    actors: List[CreateTechniquesActorsIn] = []
    is_subtechnique: bool = False


class CreateTechniquesOut(BaseModel):
    id: str = Field(None, alias='_id')
    references: List[CreateTechniquesReferencesIn]
    platforms: List[str]
    kill_chain_phases: List[str]
    permissions_required: List[str] = None
    technique_id: str
    magma: CreateTechniquesMagmaIn = None
    name: str
    description: str = None
    data_sources: List[str]
    data_sources_available: List[str] = []
    detection: str = None
    actors: List[CreateTechniquesActorsIn] = []

    @validator('id', pre=True, always=True)
    def _get_id(cls, v):
        return v['$oid']
