# Setting shared configuration variables for celery agents and API
import os

config = {
    'CELERY_BACKEND': os.getenv('RT_CELERY_BACKEND', 'redis://localhost:6379'),
    'CELERY_BROKER': os.getenv('RT_CELERY_BROKER', 'redis://localhost:6379'),
    'CORS_ALLOW_ORIGIN': os.getenv('RT_CORS_ALLOW_ORIGIN', 'https://reternal.local:8443'),
    'MONGO_HOST': os.getenv('RT_MONGO_HOST', 'localhost'),
    'MONGO_USERNAME': os.getenv('RT_MONGO_USERNAME'),
    'MONGO_PASSWORD': os.getenv('RT_MONGO_PASSWORD'),
    'MONGO_DB': os.getenv('RT_MONGO_DB', 'reternal'),
    'SERVICE_TOKEN': os.getenv('RT_SERVICE_TOKEN'),
    'OAUTH2_URL_TOKEN': os.getenv('RT_OAUTH2_URL_TOKEN'),
    'OAUTH2_CLIENT_ID': os.getenv('RT_OAUTH2_CLIENT_ID'),
    'OAUTH2_KEYS_URL': os.getenv('RT_OAUTH2_KEYS_URL', 'https://login.microsoftonline.com/common/discovery/keys')
}

routes = {
    'api.*': {
        'queue': os.getenv('RT_API_ROUTE', 'api')
    },
    'c2.*': {
        'queue': os.getenv('RT_C2_ROUTE', 'c2')
    },
    'search.*': {
        'queue': os.getenv('RT_SEARCH_ROUTE', 'search')
    }
}
