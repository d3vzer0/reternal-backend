
from pydantic import BaseModel, validator, Field
from typing import List, Dict
from datetime import datetime

class ResultsIn(BaseModel):
    end_date: datetime = Field(None, alias='date')
    agent: str
    message: str
    integration: str
    external_id: str

    @validator('end_date', pre=True, always=True)
    def _get_end_date(cls, v):
        return str(datetime.fromtimestamp(v))


class ResultsOut(BaseModel):
    end_date: str
    agent: str
    message: str
    integration: str
    external_id: str
    response: int
    data: str = None

    @validator('end_date', pre=True, always=True)
    def _get_end_date(cls, v):
        return str(v)

    @validator('data', pre=True, always=True)
    def _get_data(cls, v, values, **kwargs):
        mapping = { 0: 'Result not saved. Task does not exist or already updated',
            1: 'Result succesfully updated' }
        return mapping[values['response']]

class ResultOut(BaseModel):
    id: str = Field(None, alias='_id')
    reference_name: str
    technique_name: str
    kill_chain_phase: str
    technique_id: str
    category: str
    end_date: str = None
    module: str
    integration: str
    external_id: str
    start_date: str
    agent: str
    task: str
    group_id: str
    external_id: str
    campaign: str
    input: Dict
    message: str = None

    @validator('end_date', pre=True, always=True)
    def _get_end_date(cls, v):
        return str(datetime.fromtimestamp(v['$date']/1000)) if v else None

    @validator('start_date', pre=True, always=True)
    def _get_start_date(cls, v):
        return str(datetime.fromtimestamp(v['$date']/1000))

    @validator('id', pre=True, always=True)
    def _get_id(cls, v):
        return v['$oid']

