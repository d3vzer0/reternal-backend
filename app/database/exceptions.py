
from starlette.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from mongoengine import errors
from app import api

@api.exception_handler(errors.ValidationError)
async def mongo_invalid_format(request, exc):
    response = {'message': 'Invalid document format'}
    return JSONResponse(status_code=400, content=response )

@api.exception_handler(errors.DoesNotExist)
async def mongo_not_found(request, exc):
    response = {'message': 'Requested document does not exist'}
    return JSONResponse(status_code=404, content=response )

@api.exception_handler(errors.NotUniqueError)
async def mongo_not_unique(request, exc):
    response = {'message': 'Document is not unique'}
    return JSONResponse(status_code=409, content=response )
