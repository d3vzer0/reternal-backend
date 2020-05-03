
from pydantic import BaseModel, validator, Field
from typing import List, Dict

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

class TaskData(BaseModel):
    name: str
    commands: List[CommandIn]
    agents: List[Agents]

class Nodes(BaseModel):
    id: str
    label: str
    taskData: TaskData

class Edges(BaseModel):
    source: str
    to: str

class Graph(BaseModel):
    nodes: List[Nodes]
    edges: List[Edges]
    name: str

class GraphsOut(BaseModel):
    id: str = Field(None, alias='_id')
    name: str = None

    @validator('id', pre=True, always=True)
    def _get_id(cls, v):
        return v['$oid']
