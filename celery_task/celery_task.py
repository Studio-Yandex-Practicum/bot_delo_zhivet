import os
import subprocess
import redis
from celery import Celery

# Redis configuration
redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_port = os.environ.get('REDIS_PORT', 6379)
redis_db = os.environ.get('REDIS_DB', 0)
redis_password = os.environ.get('REDIS_PASSWORD')
redis_instance = redis.Redis(host=redis_host, port=redis_port, db=redis_db, password=redis_password)

# Celery configuration
app = Celery('tasks', broker=f"redis://{redis_host}:{redis_port}/{redis_db}")
app.conf.update(
    task_serializer='pickle',
    result_serializer='pickle',
    accept_content=['pickle'],
    timezone='Europe/Moscow'
)

@app.task
def dump_postgres_database(database_name, key_prefix='database_dump'):
    """Dumps a PostgreSQL database to a file using the pg_dump tool, and saves it to a Redis instance."""
    POSTGRES_DB = "delo_zhivet"
    POSTGRES_USER = "admin_delo_zhivet"
    POSTGRES_PASSWORD = "RJlcSxU&5c9c3L!P7h"
    DB_HOST = "localhost"
    DB_PORT = "5432"
    dump_file = os.path.join(os.getcwd(), 'my_dump_database.sql')
    os.makedirs(os.path.dirname(dump_file), exist_ok=True)

    cmd = [
        'docker', 'exec', 'db-local', 'pg_dump',
        f'--dbname=postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{POSTGRES_DB}',
        '--clean', '--if-exists', f'--file={dump_file}'
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"pg_dump command returned non-zero exit status: {e.returncode}")

    with open(dump_file, 'rb') as f:
        file_contents = f.read()
        key = f"{key_prefix}:{database_name}"
        redis_instance.set(key, file_contents)

    return f"Database dump saved to {dump_file} and Redis key {key}"


if __name__ == '__main__':
    dump_postgres_database('database_dump').delay()
