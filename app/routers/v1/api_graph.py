from typing import List
from fastapi import APIRouter, Security
from app.utils.depends import validate_token
from app.schemas.graphs import Graph, GraphsOut
from app.database.models.graphs import Graphs
import json

router = APIRouter()

@router.post('/graphs', dependencies=[Security(validate_token, scopes=['write:content'])])
async def create_graph(graph: Graph):
    ''' Save a new campaign as a graph object '''
    save_graph = Graphs.create(graph.dict())
    return save_graph

@router.get('/graphs', response_model=List[GraphsOut], dependencies=[Security(validate_token)])
async def get_graphs():
    ''' Get existing graphs '''
    all_graphs = json.loads(Graphs.objects().to_json())
    return all_graphs
