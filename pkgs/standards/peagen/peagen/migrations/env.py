import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import AsyncEngine

from sqlalchemy.ext.asyncio import create_async_engine
import os
from peagen.orm import Base

pg_dsn = os.environ.get("PG_DSN")
pg_host = os.environ.get("PG_HOST")
pg_port = os.environ.get("PG_PORT", "5432")
pg_db = os.environ.get("PG_DB")
pg_user = os.environ.get("PG_USER")
pg_pass = os.environ.get("PG_PASS")

if pg_dsn:
    if pg_dsn.startswith("postgresql://"):
        dsn = pg_dsn.replace("postgresql://", "postgresql+asyncpg://", 1)
    else:
        dsn = pg_dsn
elif pg_host and pg_db and pg_user:
    dsn = f"postgresql+asyncpg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
else:
    dsn = "sqlite+aiosqlite:///./gateway.db"

engine_kwargs = {
    "pool_size": 10,
    "max_overflow": 20,
    "echo": False,
}
if dsn.startswith("sqlite"):
    engine_kwargs["execution_options"] = {"schema_translate_map": {"peagen": None}}

engine = create_async_engine(dsn, **engine_kwargs)

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
        await conn.run_sync(Base.metadata.create_all)
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
