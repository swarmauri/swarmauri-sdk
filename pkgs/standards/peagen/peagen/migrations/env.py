import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import AsyncEngine

from sqlalchemy.ext.asyncio import create_async_engine
import os
from peagen.orm import Base

engine = create_async_engine(
    dsn,
    pool_size=10,
    max_overflow=20,
    echo=False,
)

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = str(engine.url)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection, target_metadata=target_metadata, compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    async def run_async_migrations(conn):
        await conn.run_sync(do_run_migrations)

    connectable = engine

    if not isinstance(connectable, AsyncEngine):
        raise RuntimeError("Expected an AsyncEngine")

    async with connectable.connect() as connection:
        await run_async_migrations(connection)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
