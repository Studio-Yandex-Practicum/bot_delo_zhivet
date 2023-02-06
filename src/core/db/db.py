import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, Column, func, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import (declarative_base, declared_attr, sessionmaker,
                            scoped_session)

from src.core.config import settings


class PreBase_admin:
    """Абстрактная модель для наследования моделей админ"""

    @declared_attr
    def __tablename__(cls):  # noqa
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    def __repr__(self):
        return f"{self.__class__.__name__}, id = {self.id}."


class PreBase:
    """Абстрактная модель для наследования"""

    @declared_attr
    def __tablename__(cls):  # noqa
        return cls.__name__.lower()

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(),
                        nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(),
                        nullable=False)
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        nullable=False,
        onupdate=func.current_timestamp(),
    )

    def __repr__(self):
        return f"{self.__class__.__name__}, id = {self.id}."


Base = declarative_base(cls=PreBase)
Base_admin = declarative_base(cls=PreBase_admin)
database_url = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@{settings.DB_HOST}:"
    f"{settings.DB_PORT}/{settings.POSTGRES_DB}"
)
engine = create_async_engine(database_url)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False, ))
Base_admin.query = db_session.query_property()
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)


async def get_async_session():
    """Генератор асинхронной сессии
    session_generator = get_async_session()
    session = await session_generator.asend(None)."""
    async with AsyncSessionLocal() as async_session:
        yield async_session
