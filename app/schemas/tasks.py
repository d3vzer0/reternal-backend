
from pydantic import BaseModel, validator, Field
from typing import List, Dict
from datetime import datetime

class TasksOut(BaseModel):
    id: str = Field(None, alias='_id')
    task: str
    campaign: str
    scheduled_date: str
    state: str
    dependencies: List[str]
    group_id: str

    @validator('id', pre=True, always=True)
    def _get_id(cls, v):
        return v['$oid']

    @validator('scheduled_date', pre=True, always=True)
    def _get_scheduled_date(cls, v):
        return str(datetime.fromtimestamp(v['$date']/1000))
