
from pydantic import BaseModel, validator, Field
from typing import List, Dict
from datetime import datetime

class AttckSubActorsOut(BaseModel):
    actor_id: str
    name: str


class AttckSubReferencesOut(BaseModel):
    external_id: str = None
    url: str = None
    source_name: str = None
    description: str = None


class AttcktechniquesMagmaOut(BaseModel):
    l1_usecase_name: str
    l1_usecase_id: str
    l2_usecase_name: str
    l2_usecase_id: str


class AttckTechniquesOut(BaseModel):
    id: str = Field(None, alias='_id')
    references: List[AttckSubReferencesOut] = []
    platforms: List[str]
    permissions_required:  List[str]
    technique_id: str
    name: str
    magma: AttcktechniquesMagmaOut = None
    description: str
    data_sources: List[str]
    data_sources_available: List[str] = []
    actors: List[AttckSubActorsOut]
    is_subtechnique: bool = False

    @validator('id', pre=True, always=True)
    def _get_id(cls, v):
        return v['$oid'] if v else None

# class AttckTechniquesOut(BaseModel):
#     id: str = Field(None, alias='_id')
#     references: List[AttckSubReferencesOut] = []
#     platforms: List[str]
#     permissions_required:  List[str]
#     technique_id: str
#     name: str
#     magma: AttcktechniquesMagmaOut = None
#     description: str
#     data_sources: List[str]
#     data_sources_available: List[str] = []
#     actors: List[AttckSubActorsOut]
#     is_subtechnique: bool = False


class AttckSubTechniquesOut(BaseModel):
    name: str
    technique_id: str
    data_sources: List[str]
    data_sources_available: List[str] = []


class AttckAggPhasesOut(BaseModel):
    id: str = Field(None, alias='_id')
    techniques: List[AttckSubTechniquesOut]

    @validator('id', pre=True, always=True)
    def _get_id(cls, v):
        return v['kill_chain_phases']


class AttckSubActorTechniques(BaseModel):
    technique_id: str
    name: str


class AttckActorOut(BaseModel):
    id: str = Field(None, alias='_id')
    actor_id: str
    name: str
    description: str
    references: List[AttckSubReferencesOut]
    aliases: List[str]
    techniques: List[AttckSubActorTechniques]

    @validator('id', pre=True, always=True)
    def _get_id(cls, v):
        return v['$oid']

