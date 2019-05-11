# Setting variables
from app import app
import datetime
import os

# Todo - set MongoDB username and Password as variables for DB
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET')
app.config['FLASK_PORT'] = int(os.getenv('FLASK_PORT', 5000))
app.config['CELERY_BACKEND'] = os.getenv('CELERY_BACKEND', 'redis://localhost:6379')
app.config['CELERY_BROKER'] = os.getenv('CELERY_BACKEND', 'redis://localhost:6379')
app.config['REDIS_IP'] = os.getenv('REDIS_IP', 'localhost')
app.config['REDIS_PORT'] = int(os.getenv('REDIS_PORT', '6379'))
app.config['REDIS_DB'] = int(os.getenv('REDIS_DB', 1))
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(minutes=10)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.config['C2_DEST'] = os.getenv('C2_DEST', 'http://127.0.0.1:9000/api/v1/ping')
app.config['CORS_DOMAIN'] = os.getenv('CORS_DOMAIN', 'http://localhost:8080')
app.config['MONGODB_SETTINGS'] = {
    'db': os.getenv('MONGO_DB', 'reternal'),
    'host': os.getenv('MONGO_IP', 'localhost'),
    'port': int(os.getenv('MONGO_PORT', 27017)),
    'username': os.getenv('MONGO_USER', 'reternal'),
    'password': os.getenv('MONGO_PASSWORD', None),
    'authentication_source': 'admin'
}
