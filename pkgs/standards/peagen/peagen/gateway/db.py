from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .runtime_cfg import settings

if settings.pg_dsn_env or (settings.pg_host and settings.pg_db and settings.pg_user):
    dsn = settings.apg_dsn
else:
    # Fallback to a local SQLite database when Postgres settings are missing
    dsn = "sqlite+aiosqlite:///./gateway.db"

engine = create_async_engine(
    dsn,
    pool_size=10,
    max_overflow=20,
    echo=False,
)
Session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


def get_db() -> AsyncSession:
    db = Session()
    try:
        yield db
    finally:
        if db:
            db.close()
