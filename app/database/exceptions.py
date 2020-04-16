
from starlette.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from mongoengine.errors import ValidationError, DoesNotExist, NotUniqueError, FieldDoesNotExist
from pymongo.errors import DuplicateKeyError
from app import api

@api.exception_handler(ValidationError)
async def mongo_invalid_format(request, exc):
    response = {'message': 'Invalid document format, invalid fields supplied'}
    print(exc)
    return JSONResponse(status_code=400, content=response )

@api.exception_handler(DoesNotExist)
async def mongo_not_found(request, exc):
    response = {'message': 'Requested document does not exist'}
    return JSONResponse(status_code=404, content=response )

@api.exception_handler(NotUniqueError)
async def mongo_not_unique(request, exc):
    response = {'message': 'Document is not unique'}
    return JSONResponse(status_code=409, content=response )

@api.exception_handler(FieldDoesNotExist)
async def mongo_field_does_not_exist(request, exc):
    print(exc)
    response = {'message': 'Invalid document format, provided field does not exist'}
    return JSONResponse(status_code=400, content=response )

@api.exception_handler(DuplicateKeyError)
async def mongo_not_unique(request, exc):
    response = {'message': 'Document is not unique'}
    return JSONResponse(status_code=409, content=response )
