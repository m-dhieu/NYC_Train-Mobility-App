#-------------------------------------------------
# File Name:   Dockerfile
# Description: Instructions to build backend image
# Author:      Monica Dhieu
#-------------------------------------------------

# use the official slim Python image for smaller footprint
FROM python:3.10-slim

# set working directory inside container
WORKDIR /app

# install system dependencies needed for building and running
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# copy requirements & install Python dependencies
COPY ./backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy backend app code
COPY ./backend/app ./app

# copy SQLite DB (if present) to working dir so default DB path works
COPY ./backend/nyc_train.db ./nyc_train.db

# copy frontend static files to match StaticFiles(directory="frontend")
COPY ./frontend ./frontend
COPY ./index.html ./index.html

# expose container port (can also be configured via environment variable)
ENV PORT=8000
EXPOSE $PORT

# command to run the FastAPI app with uvicorn server
# use shell form so the $PORT env var is respected at runtime
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers"]

