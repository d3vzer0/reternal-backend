# Setting variables
from app import app
import os

# Todo - set MongoDB username and Password as variables for DB
app.config['SECRET_KEY'] = os.environ["FLASK_SECRET"]
app.config['JWT_SECRET_KEY'] = os.environ["JWT_SECRET"]
app.config['MONGODB_SETTINGS'] = {
    'db': os.environ["MONGO_DB"],
    'host': os.environ["MONGO_IP"],
    'port': int(os.environ["MONGO_PORT"])
}

app.config.update(
    CELERY_BROKER_URL=os.environ["CELERY_BROKER"],
    result_backend=os.environ["CELERY_BACKEND"]
)

