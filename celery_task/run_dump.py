from celery_task import dump_postgres_database

if __name__ == '__main__':
    dump_postgres_database.delay('database_dump')
