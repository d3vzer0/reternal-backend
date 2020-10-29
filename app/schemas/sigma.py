
from pydantic import BaseModel, validator, Field, root_validator
from app.schemas.attck import AttckTechniquesOut
from app.database.models.techniques import Techniques
from typing import List, Dict, Optional
from datetime import datetime
import json
import hashlib
import re

class SigmaActorsOut(BaseModel):
    actor_id: str
    name: str


class SigmaMagmaOut(BaseModel):
    l1_usecase_name: str
    l1_usecase_id: str
    l2_usecase_name: str
    l2_usecase_id: str


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



class SigmaRule(BaseModel):
    class Config:
        allow_population_by_field_name = True
        ignore_extra = True

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

    @validator('date', pre=True, always=True)
    def _get_date(cls, v):
        return str(datetime.fromtimestamp(v['$date']/1000))


class SigmaRules(BaseModel):
    each_rule: List[SigmaRule]
    

# class SigmaRulesAlias(MyModel):
#     class Config:
#         fields = {'fields': {'alias': 'sigma_fields'}}


class SigmaIn(BaseModel):
    title: str 
    id: str = Field(..., alias='id')
    techniques: Optional[List]
    hash: str = None
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

    @root_validator(pre=True)
    def _get_techniques(cls, values):
        related_techniques = [Techniques.objects(references__external_id=tag[-5:].upper()).first() for tag in values.get('tags', [])
            if re.match(r'attack\.t[0-9]{4}', tag)]
        values['techniques'] = [json.loads(technique.to_json()) for technique  in related_techniques if technique]
        return values

    @root_validator(pre=True)
    def _generate_hash(cls, values):
        values['hash'] = hashlib.sha256(str({'sigma_id': values['id'], **values['logsource'],
            **values['detection']}).encode()).hexdigest()
        return values

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

class SigmaSearchOut(BaseModel):
    total: int
    results: List[SigmaOut]