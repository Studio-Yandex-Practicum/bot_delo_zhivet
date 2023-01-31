import uuid

from sqlalchemy import Column, DateTime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, declared_attr, sessionmaker, scoped_session
from sqlalchemy.dialects.postgresql import UUID

from src.core.config import settings


class PreBase:
    """init class add table name and id field."""

    @declared_attr
    def __tablename__(cls):  # noqa
        return cls.__name__.lower()

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    def __repr__(self):
        return f"{self.__class__.__name__}, id = {self.id}."


Base = declarative_base(cls=PreBase)

database_url = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@{settings.DB_HOST}:"
    f"{settings.DB_PORT}/{settings.POSTGRES_DB}"
)
engine = create_async_engine(database_url)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,))
Base.query = db_session.query_property()

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)


async def get_async_session():
    """Генератор асинхронной сессии
    session_generator = get_async_session()
    session = await session_generator.asend(None)."""
    async with AsyncSessionLocal() as async_session:
        yield async_session
