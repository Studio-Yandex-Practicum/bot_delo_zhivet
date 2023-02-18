from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from admin.config import Config
from src.core.db.db import Base

db = SQLAlchemy()
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, pool_size=10000,
                       max_overflow=100)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base.query = db_session.query_property()
