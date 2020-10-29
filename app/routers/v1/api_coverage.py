from app.database.models.products import Products
from app.schemas.products import ProductsIn, ProductOut
from fastapi import APIRouter

router = APIRouter()

@router.post('/products', response_model=ProductOut)
async def create_product(product: ProductsIn):
    ''' Create new product mapping '''
    create_product = Products().create(**product.dict())
    return create_product
