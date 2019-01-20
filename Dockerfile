FROM python:3.6

RUN apt-get update && apt-get -y upgrade && apt-get -y install gcc python3-dev

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Make sure to define the JWT_SECRET and FLASK_SECRET in 
# the docker(compose) configuration. ie:
# ENV JWT_SECRET
# ENV FLASK_SECRET

ARG CELERY_BROKER=redis://redis-service:6379
ENV CELERY_BROKER="${CELERY_BROKER}"

ARG CELERY_BACKEND=redis://redis-service:6379
ENV CELERY_BACKEND="${CELERY_BACKEND}"

ARG REDIS_IP=redis-service
ENV REDIS_IP="${REDIS_IP}"

ARG REDIS_PORT=6379
ENV REDIS_PORT="${REDIS_PORT}"

ARG REDIS_DB=1
ENV REDIS_DB="${REDIS_DB}"

ARG FLASK_PORT=5000
ENV FLASK_PORT="${FLASK_PORT}"

ARG MONGO_DB=reternal
ENV MONGO_DB="${MONGO_DB}"

ARG MONGO_IP=mongodb
ENV MONGO_IP="${MONGO_IP}"

ARG MONGO_PORT=27017
ENV MONGO_PORT="${MONGO_PORT}"

ARG FLASK_PORT=5000
ENV FLASK_PORT="${FLASK_PORT}"

ARG CORS_DOMAIN=http://localhost
ENV CORS_DOMAIN="${CORS_DOMAIN}"

COPY . /reternal-backend
WORKDIR /reternal-backend

CMD python run.py



