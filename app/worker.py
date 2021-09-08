import os
import json
import urllib.parse as urlparse

from celery import Celery
import psycopg2


POSTGRES_URI = urlparse.urlparse(os.environ["POSTGRES_URI"])
POSTGRES_USER = POSTGRES_URI.username
POSTGRES_PASSWORD = POSTGRES_URI.password
POSTGRES_HOST = POSTGRES_URI.hostname
POSTGRES_PORT = POSTGRES_URI.port
POSTGRES_DATABASE = POSTGRES_URI.path[1:]

BROKER_DIR = "/tmp/broker"


for f in ["out", "processed"]:
    if not os.path.exists(os.path.join(BROKER_DIR, f)):
        os.makedirs(os.path.join(BROKER_DIR, f))


app = Celery("worker")
app.conf.update(
    {
        "broker_url": "filesystem://",
        "broker_transport_options": {
            "data_folder_in": os.path.join(BROKER_DIR, "out"),
            "data_folder_out": os.path.join(BROKER_DIR, "out"),
            "data_folder_processed": os.path.join(BROKER_DIR, "processed"),
        },
        "result_persistent": False,
        "task_serializer": "json",
        "result_serializer": "json",
        "accept_content": ["json"],
    }
)


def connect_db():
    return psycopg2.connect(
        dbname=POSTGRES_DATABASE,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
    )


def create_table():
    conn = connect_db()
    sql = """
      CREATE TABLE errors (
        id BIGSERIAL PRIMARY KEY,
        error_id VARCHAR GENERATED ALWAYS AS (md5(exception::TEXT || frames::TEXT || message::TEXT)) STORED NOT NULL,
        timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT(NOW() AT TIME ZONE 'utc') NOT NULL,
        exception JSONB NOT NULL,
        message JSONB NOT NULL,
        frames JSONB NOT NULL,
        custom JSONB,
        notifier JSONB,
        server JSONB,
        platform VARCHAR,
        environment VARCHAR,
        language VARCHAR,
        level VARCHAR
      );
      CREATE INDEX idx_errors_timestamp ON errors(timestamp);
      CREATE INDEX idx_errors_error_id ON errors(error_id);
      CREATE INDEX idx_errors_environment ON errors(environment);
    """
    with conn.cursor() as curs:
        curs.execute(sql)
    conn.commit()
    conn.close()


try:
    create_table()
except Exception as e:
    print(e)


@app.task(bind=True)
def write_to_db(self, data):
    conn = connect_db()
    message = data.get("body", {}).get("message", {})
    exception = data.get("body", {}).get("trace", {}).get("exception", {})
    frames = data.get("body", {}).get("trace", {}).get("frames", [])
    with conn.cursor() as curs:
        res = curs.execute(
            """
  INSERT INTO
    errors (
        exception,
        message,
        frames,
        custom,
        notifier,
        server,
        platform,
        environment,
        language,
        level
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
            (
                json.dumps(exception),
                json.dumps(message),
                json.dumps(frames),
                json.dumps(data.get("custom", {})),
                json.dumps(data.get("notifier", {})),
                json.dumps(data.get("server", {})),
                data.get("platform"),
                data.get("environment"),
                data.get("language"),
                data.get("level"),
            ),
        )
        conn.commit()
        conn.close()
