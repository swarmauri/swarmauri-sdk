import os
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool                # only for SQLite
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker, AsyncSession
)


# ---------------------------------------------------------------------
# 1. BLOCKING  •  SQLite
# ---------------------------------------------------------------------
def blocking_sqlite_engine(path: str | None = None):
    """
    Parameters
    ----------
    path : str | None
        • None  → single shared in-memory DB (thread-safe).
        • "./db.sqlite3" etc. → file-backed database.
    """
    if path is None:
        url = "sqlite+pysqlite://"
        kwargs = dict(
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,          # same connection everywhere
            echo=False, future=True
        )
    else:
        url = f"sqlite+pysqlite:///{path}"
        kwargs = dict(echo=False, future=True)

    eng = create_engine(url, **kwargs)
    return eng, sessionmaker(bind=eng, expire_on_commit=False)


# ---------------------------------------------------------------------
# 2. ASYNC  •  SQLite  (aiosqlite driver)
# ---------------------------------------------------------------------
def async_sqlite_engine(path: str | None = None):
    url = "sqlite+aiosqlite://"
    if path:
        url += f"/{path}"

    eng = create_async_engine(
        url,
        connect_args={"check_same_thread": False},    # required by SQLite
        poolclass=StaticPool,
        echo=False,
    )
    return eng, async_sessionmaker(
        eng, expire_on_commit=False, class_=AsyncSession
    )


# ---------------------------------------------------------------------
# 3. BLOCKING  •  PostgreSQL  (psycopg2)
# ---------------------------------------------------------------------
def blocking_postgres_engine(
    user: str     = "app",
    pwd:  str     = os.getenv("PGPASSWORD", "secret"),
    host: str     = "localhost",
    port: int     = 5432,
    db:   str     = "app_db",
    pool_size: int = 10,
    max_overflow: int = 20,
):
    url = f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"
    eng = create_engine(
        url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=True,        # drops stale connections
        echo=False,
        future=True
    )
    return eng, sessionmaker(bind=eng, expire_on_commit=False)


# ---------------------------------------------------------------------
# 4. ASYNC  •  PostgreSQL  (asyncpg)
# ---------------------------------------------------------------------
def async_postgres_engine(
    user: str     = "app",
    pwd:  str     = os.getenv("PGPASSWORD", "secret"),
    host: str     = "localhost",
    port: int     = 5432,
    db:   str     = "app_db",
    pool_size: int = 10,           # initial pool size
    max_size:  int = 20,           # max pool size
):
    url = f"postgresql+asyncpg://{user}:{pwd}@{host}:{port}/{db}"
    eng = create_async_engine(
        url,
        pool_size=pool_size,
        max_overflow=max_size - pool_size,
        pool_pre_ping=True,
        echo=False,
    )
    return eng, async_sessionmaker(
        eng, expire_on_commit=False, class_=AsyncSession
    )
