from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .runtime_cfg import settings


if settings.pg_dsn_env or (settings.pg_host and settings.pg_db and settings.pg_user):
    dsn = settings.apg_dsn
else:
    # Fallback to a local SQLite database when Postgres settings are missing
    dsn = "sqlite+aiosqlite:///./authn.db"

engine = create_async_engine(
    dsn,
    pool_size=10,
    max_overflow=20,
    echo=False,
)
Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_async_db() -> AsyncSession:
    async with Session() as db:
        yield db
