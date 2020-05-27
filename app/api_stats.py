from app import api, celery, oauth2_scheme
from app.utils.depends import validate_worker
from app.schemas.user import User
from fastapi import Depends, Body
from database.models import Techniques, Coverage, Validations
from bson.json_util import dumps
from typing import List, Dict
import json



def fake_decode_token(token):
    return User(
        username=token + "fakedecoded", email="john@example.com", full_name="John Doe"
    )

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    return user

@api.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@api.get("/items/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}

@api.get('/api/v1/stats/count')
async def stats_count():
    ''' Get total count of mapped datasources '''
    stats_count = {
        'coverage': len(Coverage.objects(enabled=True)),
        'techniques': len(Techniques.objects()),
        'validations':  len(Validations.objects())
    }
    return stats_count
