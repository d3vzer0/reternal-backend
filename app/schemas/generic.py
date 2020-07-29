
from pydantic import BaseModel

class CeleryTask(BaseModel):
    task: str
