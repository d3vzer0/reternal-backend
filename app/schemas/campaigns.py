
from pydantic import BaseModel, validator, Field
from typing import List, Dict
from datetime import datetime


class Tasks(BaseModel):
    id: str = Field(None, alias='_id')
    task: str
    campaign: str
    start_date: str
    state: str
    dependencies: List[str]
    group_id: str

    @validator('id', pre=True, always=True)
    def _get_id(cls, v):
        return str(v)

    @validator('start_date', pre=True, always=True)
    def _get_start_date(cls, v):
        return str(v.strftime("%Y-%m-%d %H:%M:%S"))


class CampaignsOut(BaseModel):
    id: str = Field(None, alias='_id')
    campaign: str
    start_date: str
    tasks: List[Tasks]

    @validator('start_date', pre=True, always=True)
    def _get_start_date(cls, v):
        return str(v.strftime("%Y-%m-%d %H:%M:%S"))
