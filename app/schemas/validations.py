
from pydantic import BaseModel, validator, Field
from app.schemas.attck import AttckTechniquesOut
from database.models import Techniques
from typing import List, Dict, Optional
from datetime import datetime
import json
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


class SigmaLogsource(BaseModel):
    category: Optional[str]
    product: Optional[str]
    service: Optional[str]
    definition: Optional[str]


class SigmaRelated(BaseModel):
    sigma_id: Optional[str] = Field(..., alias='id')
    relation_type: Optional[str] = Field(..., alias='type')

    @validator('relation_type')
    def _validate_relation_type(cls, v):
        if v not in ('derived', 'obsoletes', 'merged', 'renamed'):
            raise ValueError('Invalid sigma type')
        return v

class SigmaIn(BaseModel):
    title: str 
    sigma_id: str = Field(..., alias='id')
    date: Optional[datetime]
    description: Optional[str]
    author: Optional[str]
    references: Optional[List[str]]
    status: Optional[str]
    logsource: SigmaLogsource
    detection: Dict
    related: SigmaRelated = None
    license: Optional[str]
    level: Optional[str]
    tags: Optional[List[str]]
    falsepositives: Optional[List[str]]
    sigma_fields: Optional[List[str]] = Field(None, alias='fields')

    @validator('status')
    def _validate_status(cls, v):
        if v not in ('stable', 'testing', 'experimental'):
            raise ValueError('Invalid sigma status')
        return v

    @validator('level')
    def _validate_level(cls, v):
        if v not in ('low', 'medium', 'high', 'critical'):
            raise ValueError('Invalid sigma level')
        return v

    @validator('date', pre=True)
    def _validate_date(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, '%Y/%m/%d')
        return v


class SigmaRelatedOut(BaseModel):
    id: Optional[str] = Field(None, alias='sigma_id')
    type: Optional[str] = Field(None, alias='relation_type')

    @validator('type')
    def _validate_relation_type(cls, v):
        if v not in ('derived', 'obsoletes', 'merged', 'renamed'):
            raise ValueError('Invalid sigma type')
        return v

class SigmaOut(BaseModel):
    title: str 
    sigma_id: str
    hash: str
    id: str = Field(None, alias='_id')
    date: Optional[datetime]
    description: Optional[str]
    author: Optional[str]
    references: Optional[List[str]]
    status:Optional[str]
    logsource: SigmaLogsource
    detection: Dict
    related: Optional[SigmaRelatedOut]
    license: Optional[str]
    level: Optional[str]
    tags: Optional[List[str]]
    falsepositives: Optional[List[str]]
    sigma_fields: Optional[List[str]] = Field(None, alias='fields')
    techniques: Optional[List[AttckTechniquesOut]] 

    @validator('date', pre=True, always=True)
    def _get_date(cls, v):
        return str(datetime.fromtimestamp(v['$date']/1000))

    @validator('id', pre=True, always=True)
    def _get_id(cls, v):
        return v['$oid']
