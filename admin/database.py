import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from admin.config import Config
from src.core.db.db import Base
from src.core.db.model import Staff, Role

db = SQLAlchemy()
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, pool_size=10000,
                       max_overflow=100)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base.query = db_session.query_property()
# Base.metadata.create_all(engine)


# def create_roles_and_superuser():
#     if len(Staff.query.all()) < 1:
#         staff = Staff(login=os.getenv('SUPER_USER_LOGIN'), email=os.getenv('SUPER_USER_EMAIL'),
#                       password=os.getenv('SUPER_USER_PASSWORD'),
#                       active=True)
#         role = Role(name='superuser', description='superuser')
#         role_admin = Role(name='admin', description='admin')
#         staff.roles.append(role)
#         db_session.add(staff)
#         db_session.add(role)
#         db_session.add(role_admin)
#         db_session.commit()
