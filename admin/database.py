import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, exc, inspect
from sqlalchemy.orm import scoped_session, sessionmaker

from admin.config import Config
from src.core.db.db import Base
from src.core.db.model import Role, Staff

from .messages import DB_COMMON_ERROR, DBAPI_ERROR

db = SQLAlchemy()
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, pool_size=10000, max_overflow=100)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base.query = db_session.query_property()

# Значение SQLALCHEMY_DATABASE_URI для логирования лучше не использовать,
# т.к. там содержатся учетные данные для подключения, потому:
db_info = f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('POSTGRES_DB')}"


def get_not_existing_required_tables(tables):
    not_existing_fileds = []
    try:
        for table in tables:
            if not inspect(engine).has_table(table):
                not_existing_fileds.append(table)
    except exc.OperationalError as error:
        raise ConnectionError(DBAPI_ERROR.format(db_info=db_info, details=str(error)))
    except Exception as error:
        raise EnvironmentError(DB_COMMON_ERROR.format(db_info=db_info, details=str(error)))
    return not_existing_fileds


def create_roles_and_superuser():

    if len(Staff.query.all()) < 1:
        staff = Staff(
            login=os.getenv("SUPER_USER_LOGIN"),
            email=os.getenv("SUPER_USER_EMAIL"),
            password=os.getenv("SUPER_USER_PASSWORD"),
            active=True,
        )
        role = Role(name="superuser", description="superuser")
        role_admin = Role(name="admin", description="admin")
        staff.roles.append(role)
        db_session.add(staff)
        db_session.add(role)
        db_session.add(role_admin)
        db_session.commit()
