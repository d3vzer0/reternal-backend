from app import api, celery
from app.utils.depends import validate_worker
from fastapi import Depends, Body, BackgroundTasks
from database.models import Products
from app.schemas.products import ProductsIn, ProductOut
from typing import List, Dict
import json


@api.post('/api/v1/products', response_model=ProductOut)
async def create_product(product: ProductsIn):
    ''' Create new product mapping '''
    create_product = Products().create(**product.dict())
    return create_product
