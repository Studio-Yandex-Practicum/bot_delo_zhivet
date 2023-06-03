import asyncio
import os
from logging.config import fileConfig

from dotenv import find_dotenv, load_dotenv
from geoalchemy2 import alembic_helpers
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine

from alembic import context
from src.core.db.base import Base

PG_DOCKER_ENV = os.getenv("PG_DOCKER_ENV", "local")

if PG_DOCKER_ENV == "dev":
    load_dotenv(find_dotenv(".env.db"))
else:
    load_dotenv(find_dotenv(".env.db.local"))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

database_url = (
    f'postgresql+asyncpg://{os.environ["POSTGRES_USER"]}:'
    f'{os.environ["POSTGRES_PASSWORD"]}@{os.environ["DB_HOST"]}:'
    f'{os.environ["DB_PORT"]}/{os.environ["POSTGRES_DB"]}'
)

config.set_main_option("sqlalchemy.url", database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support

# Присвоим переменной target_metadata объект класса MetaData из Base.
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=alembic_helpers.include_object,
        process_revision_directives=alembic_helpers.writer,
        render_item=alembic_helpers.render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,
        include_object=alembic_helpers.include_object,
        process_revision_directives=alembic_helpers.writer,
        render_item=alembic_helpers.render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
