from pydantic import BaseModel, validator, Field
from typing import List, Dict, Optional
from datetime import datetime


class User(BaseModel):
    username: str
    email: Optional[str] = None
    disabled: Optional[bool] = None