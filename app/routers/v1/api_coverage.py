from app.database.models.products import Products, Indices
from app.schemas.products import ProductsIn, ProductOut
from app.schemas.searchcoverage import IndexesIn, IndicesOut
from app.utils.depends import validate_token
from fastapi import APIRouter, Security

router = APIRouter()

@router.post('/products', response_model=ProductOut, dependencies=[Security(validate_token, scopes=['write:integrations'])])
async def create_product(product: ProductsIn):
    ''' Create new product mapping '''
    create_product = Products().create(**product.dict())
    return create_product


@router.post('/coverage/indexes', response_model=IndicesOut, dependencies=[Security(validate_token, scopes=['write:content'])])
async def create_index(indexes: IndexesIn):
    ''' Create datasources/index entry '''
    create_index = Indices().create(**indexes.dict())
    return create_index
