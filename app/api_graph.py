from app import api
from typing import List, Dict
from app.utils.depends import validate_worker
from app.schemas import Graph, GraphsOut
from app.database.models import Graphs
from fastapi import Depends, Body
from datetime import datetime, timedelta
import json


@api.post('/api/v1/graphs')
async def create_graph(graph: Graph):
    ''' Save a new campaign as a graph object '''
    save_graph = Graphs.create(graph.dict())
    return save_graph

@api.get('/api/v1/graphs', response_model=List[GraphsOut])
async def get_graphs():
    ''' Get existing graphs '''
    all_graphs = json.loads(Graphs.objects().to_json())
    return all_graphs
