import uvicorn
import os

FASTAPI_HOST = os.getenv('FASTAPI_HOST', '127.0.0.1')
FASTAPI_PORT = int(os.getenv('FASTAPI_PORT', 5000))
FASTAPI_DEBUG =  (os.getenv('FASTAPI_DEBUG', "True") == "True")
   
if __name__ == "__main__":
    uvicorn.run("app:api", host=FASTAPI_HOST, port=FASTAPI_PORT,
        log_level="info", reload=FASTAPI_DEBUG)
