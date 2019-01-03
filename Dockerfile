FROM python:3.6

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Make sure to define the JWT_SECRET and FLASK_SECRET in 
# the docker(compose) configuration. ie:
# ENV JWT_SECRET
# ENV FLASK_SECRET

ARG MONGO_DB=redis://redis_service:6379
ENV MONGO_DB="${MONGO_DB}"

ARG MONGO_IP=redis://redis_service:6379
ENV MONGO_IP="${MONGO_IP}"

ARG MONGO_PORT=redis://redis_service:6379
ENV MONGO_PORT="${MONGO_PORT}"

COPY . /reternal-backend
WORKDIR /reternal-backend

CMD python run.py



