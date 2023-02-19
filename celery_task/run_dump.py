import os
from celery_task import dump_postgres_database

if __name__ == '__main__':
    dump_postgres_database.delay(os.getenv('POSTGRES_DB'))
