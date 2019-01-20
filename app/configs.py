# Setting variables
from app import app
import datetime
import os

# Todo - set MongoDB username and Password as variables for DB
app.config['SECRET_KEY'] = os.environ["FLASK_SECRET"]
app.config['FLASK_PORT'] = int(os.environ['FLASK_PORT'])
app.config['CELERY_BACKEND'] = os.environ["CELERY_BACKEND"]
app.config['CELERY_BROKER'] = os.environ['CELERY_BROKER']
app.config['REDIS_IP'] = os.environ['REDIS_IP']
app.config['REDIS_PORT'] = int(os.environ['REDIS_PORT'])
app.config['REDIS_DB'] = int(os.environ['REDIS_DB'])
app.config['JWT_SECRET_KEY'] = os.environ["JWT_SECRET"]
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(minutes=10)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.config['CORS_DOMAIN'] = os.environ['CORS_DOMAIN']
app.config['MONGODB_SETTINGS'] = {
    'db': os.environ["MONGO_DB"],
    'host': os.environ["MONGO_IP"],
    'port': int(os.environ["MONGO_PORT"])
}

