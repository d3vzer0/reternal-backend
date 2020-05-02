
from pydantic import BaseModel, validator, Field
from typing import List, Dict
from datetime import datetime


class Tasks(BaseModel):
    id: str = Field(None, alias='_id')
    task: str
    campaign: str
    scheduled_date: str
    state: str
    dependencies: List[str]
    group_id: str

    @validator('id', pre=True, always=True)
    def _get_id(cls, v):
        return str(v)

    @validator('scheduled_date', pre=True, always=True)
    def _get_scheduled_date(cls, v):
        return str(v.strftime("%Y-%m-%d %H:%M:%S"))


class CampaignsOut(BaseModel):
    id: str = Field(None, alias='_id')
    campaign: str
    scheduled_date: str
    tasks: List[Tasks]

    @validator('scheduled_date', pre=True, always=True)
    def _get_scheduled_date(cls, v):
        return str(v.strftime("%Y-%m-%d %H:%M:%S"))


class CommandIn(BaseModel):
    reference: str = None
    reference_name: str = None
    technique_name: str = None
    kill_chain_phase: str = None
    technique_id: str = None
    category: str
    integration: str
    module: str
    input: Dict
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
