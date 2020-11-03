FROM python:3.8-slim

RUN apt-get update && apt-get -y upgrade && apt-get -y install gcc python3-dev
RUN pip3 install virtualenv

RUN useradd -ms /bin/bash reternal
USER reternal
WORKDIR /home/reternal

ENV VIRTUAL_ENV=/home/reternal/venv
RUN virtualenv -p python3 $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Make sure to define the JWT_SECRET and FLASK_SECRET in 
# the docker(compose) configuration. ie:
# ENV JWT_SECRET
# ENV FLASK_SECRET

ARG FASTAPI_DEBUG=False
ENV FASTAPI_DEBUG="${FASTAPI_DEBUG}"

ARG REDIS_IP=redis
ENV REDIS_IP="${REDIS_IP}"

ARG REDIS_PORT=6379
ENV REDIS_PORT="${REDIS_PORT}"

ARG REDIS_DB=1
ENV REDIS_DB="${REDIS_DB}"

ARG FASTAPI_PORT=5000
ENV FASTAPI_PORT="${FASTAPI_PORT}"

ARG MONGO_DB=reternal
ENV MONGO_DB="${MONGO_DB}"

ARG MONGO_IP=mongodb
ENV MONGO_IP="${MONGO_IP}"

ARG MONGO_PORT=27017
ENV MONGO_PORT="${MONGO_PORT}"

ARG FASTAPI_HOST=0.0.0.0
ENV FASTAPI_HOST="${FASTAPI_HOST}"

ARG CORS_DOMAIN=http://localhost
ENV CORS_DOMAIN="${CORS_DOMAIN}"

ADD . /home/reternal/

ENTRYPOINT ["python", "run.py"]



