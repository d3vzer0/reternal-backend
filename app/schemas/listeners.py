
from pydantic import BaseModel, validator, Field
from typing import List, Dict

class ListenersOut(BaseModel):
    id: str
    name: str
    integration: str
    listener_type: str
    options: Dict
