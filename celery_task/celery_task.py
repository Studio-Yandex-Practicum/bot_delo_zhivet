import os
import subprocess
from pathlib import Path

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
    db_user = os.getenv('POSTGRES_USER')
    db_password = os.getenv('POSTGRES_PASSWORD')
    db_host = os.getenv('POSTGRES_HOST')
    db_port = os.getenv('POSTGRES_PORT')
    dump_file = Path(f'{Path(__file__).parent}/databasedump/{database_name}.sql')
    cmd = [
        'pg_dump',
        f'--dbname=postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{database_name}',
        '--clean',
        '--if-exists',
        f'--file={dump_file}',
    ]
    subprocess.run(cmd, check=True)

    with open(dump_file, 'rb') as f:
        file_contents = f.read()
        key = f"{key_prefix}:{database_name}"
        redis_instance.set(key, file_contents)

    return str(dump_file)


if __name__ == '__main__':
    dump_postgres_database('my_database').delay()
