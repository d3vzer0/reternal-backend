from app.database.models.products import Products
from app.schemas.products import ProductsIn, ProductOut
from app.utils.depends import validate_token
from fastapi import APIRouter, Security

router = APIRouter()

@router.post('/products', response_model=ProductOut, dependencies=[Security(validate_token, scopes=['write:integrations'])])
async def create_product(product: ProductsIn):
    ''' Create new product mapping '''
    create_product = Products().create(**product.dict())
    return create_product
