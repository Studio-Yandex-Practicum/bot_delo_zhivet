# For example, to use the script create a crontab task (crontab -e) scheduled at 3 a.m every day:
# 0 3 * * * python3 /home/user/bot_delo_zhivet/src/core/db/backup/task.py
# or to check it you can create task like
# * * * * * python3 /home/user/bot_delo_zhivet/src/core/db/backup/task.py
# This line creates dump_fiele everyminute

import os
import subprocess
from datetime import date


# from dotenv import load_dotenv
# load_dotenv('.env')

# POSTGRES_USER = os.environ["POSTGRES_USER"]
# POSTGRES_DB = os.environ["POSTGRES_DB"]
# POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]

POSTGRES_DB = "delo_zhivet"
POSTGRES_USER = "admin_delo_zhivet"
POSTGRES_PASSWORD = "RJlcSxU&5c9c3L!P7h"

def backup():

    # db_backup file is created in the user's home directory
    dump_file = os.path.join(os.getcwd(), f'db_backup_{date.today()}.sql')

    dump_command = (
        'docker exec -i db '
        f'usr/local/bin/pg_dump -U {POSTGRES_USER} '
        f'{POSTGRES_DB} > {dump_file}'
    )
    try:
        subprocess.call(dump_command, shell=True)
        print(f'Backup is created. {dump_file}')
    except subprocess.CalledProcessError as e:
        print(f"pg_dump command returned non-zero exit status: {e.returncode}")


if __name__ == '__main__':
    backup()
