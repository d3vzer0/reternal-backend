from pydantic import BaseModel, validator, Field
from typing import List, Dict
from app.database.models.techniques import Techniques
from datetime import datetime


class ProductConfiguration(BaseModel):
    name: str = None
    vendor: str = None
    sourcetype: str = None
    source: str = None
    index: str = None

class DataQuality(BaseModel):
    device_completeness: int = 0
    field_completeness: int = 0
    timeliness: int = 0
    consistency: int = 0
    retention: int = 0

class CoverageOut(BaseModel):
    id: str = Field(None, alias='_id')
    data_quality: DataQuality = {}
    products: List[ProductConfiguration] = []
    data_source_name: str = None
    date_registered: str = None
    date_connected: str = None
    available_for_data_analytics: bool = False
    enabled: bool = False
    comment: str = ''

    @validator('products', pre=True, always=True)
    def _products(cls, v):
        defaults = []
        return v if v else defaults

    @validator('data_quality', pre=True, always=True)
    def _data_quality(cls, v):
        defaults = {'device_completeness': 0, 'field_completeness': 0,
            'timeliness': 0, 'consistency': 0, 'retention': 0}
        return v if v else defaults

    @validator('date_registered', pre=True, always=True)
    def _get_date_registered(cls, v):
        return str(datetime.fromtimestamp(v['$date']/1000)) if v else None

    @validator('date_connected', pre=True, always=True)
    def _get_date_connected(cls, v):
        return str(datetime.fromtimestamp(v['$date']/1000)) if v else None

    @validator('id', pre=True, always=True)
    def _get_id(cls, v):
        return v['$oid']

class CoverageIn(BaseModel):
    data_quality: DataQuality = None
    products: List[ProductConfiguration] = None
    data_source_name: str
    date_registered: datetime = None
    date_connected: datetime = None
    available_for_data_analytics: bool = False
    enabled: bool = False
    comment: str = ''

    @validator('data_source_name')
    def _data_source_must_be_available(cls, v):
        if v not in [ds for ds in Techniques.objects().distinct('data_sources') if ds]:
            raise ValueError('Invalid data_source_name')
        return v

  