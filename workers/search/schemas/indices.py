from pydantic import BaseModel, validator, Field
from typing import List, Dict
from datetime import datetime

class IndicesIn(BaseModel):
    index: str
    source: str
    sourcetype: str


class IndiceList(BaseModel):
    indices: List[IndicesIn]
    integration: str
    execution_date: datetime

    @validator('execution_date', pre=True, always=True)
    def _get_execution_date(cls, v):
        return datetime.strptime(v, '%Y-%m-%dT%H:%M:%S.%f')

