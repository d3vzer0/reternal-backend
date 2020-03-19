from pydantic import BaseModel, validator, Field
from typing import List, Dict
from datetime import datetime

class CommandIn(BaseModel):
    reference: str = None
    reference_name: str = None
    technique_name: str = None
    kill_chain_phase: str = None
    technique_id: str = None
    category: str
    module: str
    input: str
    sleep: str = 1


class Agents(BaseModel):
    name: str
    integration: str
    id: str

class TaskIn(BaseModel):
    name: str
    sleep: int
    start_date: datetime
    commands: List[CommandIn]
    agents: List[Agents]

class DependencyIn(BaseModel):
    source: str
    destination: str

class CampaignIn(BaseModel):
    name: str
    tasks: List[TaskIn]
    dependencies: List[DependencyIn]


class TaskOut(BaseModel):
    name: str
    start_date: str
    state: str

    @validator('start_date', pre=True, always=True)
    def _get_start_date(cls, v):
        return str(datetime.fromtimestamp(v['$date']/1000))

class CampaignOut(BaseModel):
    id: str = Field(None, alias='_id')
    name: str = None
    tasks: List[TaskOut] = [ ]

    @validator('id', pre=True, always=True)
    def _get_id(cls, v):
        return v['$oid']

class CampaignsOut(BaseModel):
    campaigns: List[CampaignOut] = [ ]


class ScheduleOut(BaseModel):
    id: str = Field(None, alias='_id')
    task: str
    start_date: str
    commands: List[CommandIn]
    state: str
    agents: List[Agents]

    @validator('start_date', pre=True, always=True)
    def _get_start_date(cls, v):
        return str(datetime.fromtimestamp(v['$date']/1000))

    @validator('id', pre=True, always=True)
    def _get_id(cls, v):
        return v['$oid']
