
from pydantic import BaseModel, validator, Field
from typing import List, Dict
from datetime import datetime

class Agents(BaseModel):
    name: str
    integration: str
    id: str


class CampaignTasksOut(BaseModel):
    name: str
    scheduled_date: str
    start_date: str = None
    end_date: str = None
    agents: List[Agents]
    dependencies: List[str]
    state: str

    @validator('scheduled_date', pre=True, always=True)
    def _get_scheduled_date(cls, v):
        return str(datetime.fromtimestamp(v['$date']/1000))

    @validator('start_date', pre=True, always=True)
    def _get_start_date(cls, v):
        return  None if not v else str(datetime.fromtimestamp(v['$date']/1000))

    @validator('end_date', pre=True, always=True)
    def _get_end_date(cls, v):
        return  None if not v else str(datetime.fromtimestamp(v['$date']/1000))


class CampaignsOut(BaseModel):
    id: str = Field(None, alias='_id')
    group_id: str
    name: str
    saved_date: str
    tasks: List[CampaignTasksOut]

    @validator('id', pre=True, always=True)
    def _get_id(cls, v):
        return v['$oid']

    @validator('saved_date', pre=True, always=True)
    def _get_saved_date(cls, v):
        return str(datetime.fromtimestamp(v['$date']/1000))

# Data input
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


class DependencyIn(BaseModel):
    source: str
    destination: str


class CampaignTaskIn(BaseModel):
    name: str
    sleep: int
    scheduled_date: datetime = None
    commands: List[CommandIn]
    agents: List[Agents]

    @validator('scheduled_date', pre=True, always=True)
    def _set_date(cls, v):
        return v or datetime.now()


class CampaignIn(BaseModel):
    name: str
    tasks: List[CampaignTaskIn]
    dependencies: List[DependencyIn]


# Filtered values for denormalization
class CampaignTaskDenomIn(BaseModel):
    name: str
    scheduled_date: datetime = None
    agents: List[Agents]

    @validator('scheduled_date', pre=True, always=True)
    def _set_date(cls, v):
        return v or datetime.now()


class CampaignDenomIn(BaseModel):
    name: str
    group_id: str
    tasks: List[CampaignTaskDenomIn]
    dependencies: List[DependencyIn]
