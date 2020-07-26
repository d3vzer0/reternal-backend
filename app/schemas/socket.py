
from pydantic import BaseModel, validator, Field
from typing import List, Dict
from datetime import datetime


class Authenticate(BaseModel):
    access_token: str