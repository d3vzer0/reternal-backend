
from pydantic import BaseModel, validator, Field
from typing import List, Dict
from datetime import datetime

class ModuleIn(BaseModel):
    agent: str
    module: str
    input: Dict

class ModulesOut(BaseModel):
    description: str
    operating_system: List[str]
    options: Dict