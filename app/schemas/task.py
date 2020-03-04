
from pydantic import BaseModel, validator, Field
from typing import List, Dict
from datetime import datetime


class TasksOut(BaseModel):
    id: str = Field(None, alias='_id')
    task: str
    campaign: str
    start_date: str
    state: str
    dependencies: List[str]

    @validator('id', pre=True, always=True)
    def _get_id(cls, v):
        return v['$oid']

    @validator('start_date', pre=True, always=True)
    def _get_start_date(cls, v):
        return str(datetime.fromtimestamp(v['$date']/1000))
