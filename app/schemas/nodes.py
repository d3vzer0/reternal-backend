
from pydantic import BaseModel, validator, Field
from typing import List, Dict, Optional


class Argument(BaseModel):
    label: str
    description: str
    form: str
    multi: str = None
    required: str
    external_options: str = None
    options: Optional[List[str]] = None

class Node(BaseModel):
    name: str
    category: str
    integration: str
    label: str
    description: str
    icon: str = None
    thumbnail: str = None
    inputs: int
    outputs: int
    task: str
    arguments: Dict[str, Argument]
