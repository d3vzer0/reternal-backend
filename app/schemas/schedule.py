
from pydantic import BaseModel, validator, Field
from typing import List, Dict
from datetime import datetime

class Agents(BaseModel):
    name: str
    integration: str
    id: str


class CommandIn(BaseModel):
    reference: str = None
    reference_name: str = None
    technique_name: str = None
    kill_chain_phase: str = None
    technique_id: str = None
    category: str
    module: str
    input: Dict
    sleep: str = 1


class PlanTaskIn(BaseModel):
    id: str = Field(None, alias='_id')
    task: str
    start_date: str
    commands: List[CommandIn]
    state: str
    agents: List[Agents]
    group_id: str
    campaign: str

class ScheduleOut(BaseModel):
    id: str = Field(None, alias='_id')
    task: str
    start_date: str
    commands: List[CommandIn]
    state: str
    agents: List[Agents]
    campaign: str
    group_id: str

    @validator('start_date', pre=True, always=True)
    def _get_start_date(cls, v):
        return str(datetime.fromtimestamp(v['$date']/1000))

    @validator('id', pre=True, always=True)
    def _get_id(cls, v):
        return v['$oid']

