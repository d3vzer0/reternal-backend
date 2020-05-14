from pydantic import BaseModel, validator, Field
from typing import List, Dict
from datetime import datetime

class LogsourceIn(BaseModel):
    first_seen: datetime = Field(..., alias='firstTime')
    last_seen: datetime = Field(..., alias='lastTime')
    sourcetype: str
    event_count: str = Field(..., alias='totalCount')

    @validator('first_seen', pre=True, always=True)
    def _get_first_seen(cls, v):
        return datetime.fromtimestamp(int(v))

    @validator('last_seen', pre=True, always=True)
    def _get_last_seen(cls, v):
        return datetime.fromtimestamp(int(v))


class LogsourceList(BaseModel):
    logsources: List[LogsourceIn]
    integration: str
    execution_date: datetime

    @validator('execution_date', pre=True, always=True)
    def _get_execution_date(cls, v):
        return datetime.strptime(v, '%Y-%m-%dT%H:%M:%S.%f')
