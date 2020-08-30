
from pydantic import BaseModel, validator, Field
from typing import List, Dict, Any
from datetime import datetime
import networkx as nx

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
    integration: str
    module: str
    input: Dict
    sleep: str = 1


class DependencyOut(BaseModel):
    source: str
    destination: str


class CampaignTaskOut(BaseModel):
    name: str
    sleep: int
    state: str
    commands: List[CommandIn]
    agent: Agents
    scheduled_date: str
    start_date: str = None
    end_date: str = None
    
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
    name: str
    state: str
    nodes: List[CampaignTaskOut]
    edges: List[DependencyOut]
    saved_date: str

    @validator('id', pre=True, always=True)
    def _get_id(cls, v):
        return v['$oid']

    @validator('saved_date', pre=True, always=True)
    def _get_saved_date(cls, v):
        return str(datetime.fromtimestamp(v['$date']/1000))

class DependencyIn(BaseModel):
    source: str
    destination: str


class CampaignTaskIn(BaseModel):
    name: str
    sleep: int
    scheduled_date: datetime = None
    commands: List[CommandIn]
    agent: Agents

    @validator('scheduled_date', pre=True, always=True)
    def _set_date(cls, v):
        return v or datetime.now()


class CampaignIn(BaseModel):
    name: str
    nodes: List[CampaignTaskIn]
    edges: List[DependencyIn]
    graph: Any = None

    @validator('graph', pre=False, always=True)
    def _set_graph(cls, v, values):
        graph = nx.DiGraph()
        print(values)
        [graph.add_node(node.name) for node in values['nodes']]
        [graph.add_edge(edge.source, edge.destination) for edge in values['edges']]
        if not nx.is_directed_acyclic_graph(graph):
            raise ValueError('Graph supplied not a directed acyclic graph')
        return graph


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


class CreateCampaignTasksOut(BaseModel):
    task: str


class ScheduledTasksOut(BaseModel):
    agent: str
    queue: List[str]


class CreateCampaignOut(BaseModel):
    campaign: str
    group_id: str
    scheduled_tasks: List[ScheduledTasksOut]
