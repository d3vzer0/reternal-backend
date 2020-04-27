                     # Setting variables
import datetime
import os

config = {
    'CELERY_BACKEND': os.getenv('RT_CELERY_BACKEND', 'redis://localhost:6379'),
    'CELERY_BROKER': os.getenv('RT_CELERY_BACKEND', 'redis://localhost:6379'),
    'MONGO_HOST': os.getenv('RT_MONGO_HOST', 'localhost')
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
    }
}


# JWT_SECRET_KEY = os.getenv('JWT_SECRET')
# JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=10)
# JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=1)
# JWT_BLACKLIST_ENABLED = True
# JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
# CORS_DOMAIN =  os.getenv('CORS_DOMAIN', 'http://localhost:8080')
# MONGODB_SETTINGS = {
#     'db': os.getenv('MONGO_DB', 'reternal'),
#     'host': os.getenv('MONGO_IP', 'localhost'),
#     'port': int(os.getenv('MONGO_PORT', 27017)),
#     'username': os.getenv('MONGO_USER', None),
#     'password': os.getenv('MONGO_PASSWORD', None),
#     'authentication_source': os.getenv('MONGO_SOURCE', 'admin')
# }
