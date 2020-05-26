FROM python:3.8-buster
WORKDIR /app
COPY requirements.txt /app
RUN pip install --no-cache-dir -r /app/requirements.txt