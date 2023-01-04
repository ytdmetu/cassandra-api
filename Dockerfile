FROM tiangolo/uvicorn-gunicorn:python3.10-slim

COPY requirements-lock2.txt /tmp/requirements.txt
RUN pip install --no-deps -r /tmp/requirements.txt

COPY . /app
RUN mv /app/app.py /app/main.py