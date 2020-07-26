
from starlette.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from mongoengine.errors import ValidationError, DoesNotExist, NotUniqueError, FieldDoesNotExist
from jwt.exceptions import (InvalidTokenError, DecodeError, InvalidSignatureError, ExpiredSignatureError,
    InvalidAudienceError, InvalidIssuerError, InvalidIssuedAtError, ImmatureSignatureError, InvalidAlgorithmError)
from pymongo.errors import DuplicateKeyError
from app.main import app

# Mongodb exceptions
@app.exception_handler(ValidationError)
async def mongo_invalid_format(request, exc):
    response = {'message': 'Invalid document format, invalid fields supplied'}
    return JSONResponse(status_code=400, content=response )

@app.exception_handler(DoesNotExist)
async def mongo_not_found(request, exc):
    response = {'message': 'Requested document does not exist'}
    return JSONResponse(status_code=404, content=response )

@app.exception_handler(NotUniqueError)
async def mongo_not_unique(request, exc):
    print(exc)
    response = {'message': 'Document is not unique'}
    return JSONResponse(status_code=409, content=response )

@app.exception_handler(FieldDoesNotExist)
async def mongo_field_does_not_exist(request, exc):
    print(exc)
    response = {'message': 'Invalid document format, provided field does not exist'}
    return JSONResponse(status_code=400, content=response )

@app.exception_handler(DuplicateKeyError)
async def mongo_not_unique(request, exc):
    response = {'message': 'Document is not unique'}
    return JSONResponse(status_code=409, content=response )


# access_token validation exceptions
@app.exception_handler(InvalidTokenError)
async def jwt_invalid_token(request, exc):
    response = {'message': 'Invalid access_token supplied'}
    return JSONResponse(status_code=400, content=response )

@app.exception_handler(DecodeError)
async def decode_error(request, exc):
    response = {'message': 'Unable to decode access_token'}
    return JSONResponse(status_code=400, content=response )

@app.exception_handler(InvalidSignatureError)
async def jwt_invalid_signature(request, exc):
    response = {'message': 'Could not validate access_token signature'}
    return JSONResponse(status_code=400, content=response )

@app.exception_handler(ExpiredSignatureError)
async def jwt_expired(request, exc):
    response = {'message': 'Expired access_token'}
    return JSONResponse(status_code=401, content=response )

@app.exception_handler(InvalidAudienceError)
async def jwt_invalid_audience(request, exc):
    response = {'message': 'Unauthorized audience for access_token'}
    return JSONResponse(status_code=401, content=response )

@app.exception_handler(InvalidIssuerError)
async def jwt_invalid_issuer(request, exc):
    response = {'message': 'Invalid issuer for access_token'}
    return JSONResponse(status_code=401, content=response )

@app.exception_handler(InvalidIssuedAtError)
async def jwt_invalid_issued_at(request, exc):
    response = {'message': 'Invalid issued date for access_token'}
    return JSONResponse(status_code=401, content=response )

@app.exception_handler(ImmatureSignatureError)
async def jwt_immature_sig(request, exc):
    response = {'message': 'Signature validation error for access_token'}
    return JSONResponse(status_code=400, content=response )

@app.exception_handler(InvalidAlgorithmError)
async def jwt_invalig_alg(request, exc):
    response = {'message': 'Invalid algorithm for access_token'}
    return JSONResponse(status_code=400, content=response )

