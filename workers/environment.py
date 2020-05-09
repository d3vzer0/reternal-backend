import os

config = {
    'CELERY_BACKEND': os.getenv('RT_CELERY_BACKEND', 'redis://localhost:6379'),
    'CELERY_BROKER': os.getenv('RT_CELERY_BACKEND', 'redis://localhost:6379'),
    'CELERY_TIMER': os.getenv('RT_CELERY_TIMER', 10.0),
    'EMPIRE_TOKEN': os.getenv('RT_TOKEN_EMPIRE'),
    'EMPIRE_PATH': os.getenv('RT_EMPIRE_PATH', 'https://localhost:1337/api/'),
    'EMPIRE_USERNAME': os.getenv('RT_EMPIRE_USERNAME'),
    'EMPIRE_PASSWORD': os.getenv('RT_EMPIRE_PASSWORD')
}
