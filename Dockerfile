FROM tiangolo/uvicorn-gunicorn:python3.10-slim

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY . /app
RUN mv /app/app.py /app/main.py