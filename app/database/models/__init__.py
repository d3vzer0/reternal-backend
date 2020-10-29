from mongoengine import connect
from app.environment import config

# Init DB
connect(db='reternal', host=config['MONGO_HOST'],
    username=config['MONGO_USERNAME'], password=config['MONGO_PASSWORD'])
