
from starlette.responses import JSONResponse
from jwt.exceptions import (InvalidTokenError, DecodeError, InvalidSignatureError, ExpiredSignatureError,
    InvalidAudienceError, InvalidIssuerError, InvalidIssuedAtError, ImmatureSignatureError, InvalidAlgorithmError)
from app.main import app

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

