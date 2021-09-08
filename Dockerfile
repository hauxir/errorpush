FROM python:3.9-slim

RUN pip install flask gunicorn celery psycopg2-binary

EXPOSE 5000

COPY app /app

WORKDIR /app

CMD bash entrypoint.sh
