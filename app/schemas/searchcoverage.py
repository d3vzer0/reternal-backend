
from pydantic import BaseModel, validator, Field
from typing import List, Dict
from datetime import datetime

class TaskOut(BaseModel):
    task: str

class SourcetypesOut(BaseModel):
    id: str = Field(None, alias='_id')
    integration: str
    execution_date: str
    first_seen: str
    last_seen: str
    sourcetype: str
    event_count: str

    @validator('execution_date', pre=True, always=True)
    def _get_execution_date(cls, v):
        return str(datetime.fromtimestamp(v['$date']/1000)) if v else None

    @validator('first_seen', pre=True, always=True)
    def _get_first_seen(cls, v):
        return str(datetime.fromtimestamp(v['$date']/1000)) if v else None

    @validator('last_seen', pre=True, always=True)
    def _get_last_seen(cls, v):
        return str(datetime.fromtimestamp(v['$date']/1000)) if v else None

    @validator('id', pre=True, always=True)
    def _get_id(cls, v):
        return v['$oid']


class IndicesOut(BaseModel):
    id: str = Field(None, alias='_id')
    index: str
    integration: str
    execution_date: str
    source: str
    sourcetype: str


    @validator('execution_date', pre=True, always=True)
    def _get_execution_date(cls, v):
        return str(datetime.fromtimestamp(v['$date']/1000)) if v else None

    @validator('id', pre=True, always=True)
    def _get_id(cls, v):
        return v['$oid']
