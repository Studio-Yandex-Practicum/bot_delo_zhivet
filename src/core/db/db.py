from sqlalchemy import Column, Integer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, declared_attr, sessionmaker

from src.core.config import settings


class PreBase:
    """init class add table name and id field."""

    @declared_attr
    def __tablename__(cls):  # noqa
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)

    def __repr__(self):
        return f"{self.__class__.__name__}, id = {self.id}."


Base = declarative_base(cls=PreBase)
database_url = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@{settings.DB_HOST}:"
    f"{settings.DB_PORT}/{settings.POSTGRES_DB}"
)
engine = create_async_engine(database_url)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)


async def get_async_session():
    """Генератор асинхронной сессии
    session_generator = get_async_session()
    session = await session_generator.asend(None)."""
    async with AsyncSessionLocal() as async_session:
        yield async_session
