celery_routes = {
    'agent.*': {
        'queue': 'agent'
    },
    'api.*': {
        'queue':'api'
    },
    'c2.*': {
        'queue':'c2'
    }
}