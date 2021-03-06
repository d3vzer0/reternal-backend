# Setting shared configuration variables for celery agents and API
import os

config = {
    'API_PATH': os.getenv('RT_API_PATH', '/api/v1'),
    'CELERY_BACKEND': os.getenv('RT_CELERY_BACKEND', 'redis://localhost:6379'),
    'CELERY_BROKER': os.getenv('RT_CELERY_BROKER', 'redis://localhost:6379'),
    'REDIS_PATH_CACHE': os.getenv('RT_REDIS_PATH_CACHE'),
    'REDIS_PATH_SOCKETIO': os.getenv('RT_REDIS_PATH_SOCKETIO'),
    'CORS_ALLOW_ORIGIN': os.getenv('RT_CORS_ALLOW_ORIGIN', 'http://localhost:9090/'),
    'MONGO_HOST': os.getenv('RT_MONGO_HOST', 'localhost'),
    'MONGO_USERNAME': os.getenv('RT_MONGO_USERNAME'),
    'MONGO_PASSWORD': os.getenv('RT_MONGO_PASSWORD'),
    'MONGO_DB': os.getenv('RT_MONGO_DB', 'reternal'),
    'SERVICE_TOKEN': os.getenv('RT_SERVICE_TOKEN'),
    'OAUTH2_ISSUER': os.getenv('RT_OAUTH2_ISSUER'),
    'OAUTH2_AUDIENCE': os.getenv('RT_OAUTH2_AUDIENCE'),
    'OAUTH2_OPENID_CONFIG': os.getenv('RT_OAUTH2_OPENID_CONFIG', 'https://login.microsoftonline.com/common/discovery/keys')
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
    },
    'nodes.*': {
        'queue': os.getenv('NODES_ROUTE', 'nodes')
    }
}
