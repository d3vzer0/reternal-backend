
from pydantic import BaseModel, validator, Field
from typing import List, Dict
from datetime import datetime

class WorkersSubFunction(BaseModel):
    get: str = None
    run: str = None
    set: str = None
    create: str = None
    delete: str = None


class WorkersOut(BaseModel):
    name: str
    description: str
    thumbnail: str = None
    platforms: List[str]
    enabled: bool
    modules: WorkersSubFunction
    agents: WorkersSubFunction
    listeners: WorkersSubFunction
    stagers: WorkersSubFunction
    tasks: WorkersSubFunction


class WorkersSearchOut(BaseModel):
    name: str
    description: str
    thumbnail: str = None
    enabled: bool
    query: WorkersSubFunction
    sourcetypes: WorkersSubFunction
    indices: WorkersSubFunction
