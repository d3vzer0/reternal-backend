from typing import List
from fastapi import APIRouter
from app.schemas.graphs import Graph, GraphsOut
from app.database.models import Graphs
import json

router = APIRouter()

@router.post('/graphs')
async def create_graph(graph: Graph):
    ''' Save a new campaign as a graph object '''
    save_graph = Graphs.create(graph.dict())
    return save_graph

@router.get('/graphs', response_model=List[GraphsOut])
async def get_graphs():
    ''' Get existing graphs '''
    all_graphs = json.loads(Graphs.objects().to_json())
    return all_graphs
