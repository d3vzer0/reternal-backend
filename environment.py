# Setting shared configuration variables for celery agents and API
import os

config = {
    'CELERY_BACKEND': os.getenv('RT_CELERY_BACKEND', 'redis://localhost:6379'),
    'CELERY_BROKER': os.getenv('RT_CELERY_BACKEND', 'redis://localhost:6379'),
    'CORS_ALLOW_ORIGIN': os.getenv('RT_CORS_ALLOW_ORIGIN', 'http://localhost:9090'),
    'MONGO_HOST': os.getenv('RT_MONGO_HOST', 'localhost'),
}

routes = {
    'agent.*': {
        'queue': os.getenv('RT_AGENT_QUEUE', 'agent')
    },
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

