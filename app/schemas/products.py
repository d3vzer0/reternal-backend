
from pydantic import BaseModel, validator, Field
from app.database.models import PLATFORMS, Techniques
from typing import List, Dict
from datetime import datetime

class ProductOut(BaseModel):
    id: str = Field(None, alias='_id')
    vendor: str
    name: str
    platforms: List[str] = []
    sourcetype: str

    @validator('id', pre=True, always=True)
    def _get_id(cls, v):
        return v['$oid']


class ProductsIn(BaseModel):
    datasources: List[str]
    vendor: str
    name: str
    platforms: List[str] = []
    sourcetype: str

    @validator('platforms')
    def _valid_platforms(cls, v):
        for platform in v:
            if not platform in PLATFORMS:
                raise ValueError('Invalid platform')
        return v

    @validator('datasources')
    def _data_source_must_be_available(cls, v):
        for datasource in v:
            if datasource not in [ds for ds in Techniques.objects().distinct('data_sources') if ds]:
                raise ValueError('Invalid datasource')
        return v