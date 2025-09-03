"""SQLAlchemy engine and sessionmaker builders."""

import os
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import StaticPool  # only for SQLite
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


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
            poolclass=StaticPool,  # same connection everywhere
            echo=False,
            future=True,
        )
    else:
        url = f"sqlite+pysqlite:///{path}"
        kwargs = dict(echo=False, future=True)

    eng = create_engine(url, **kwargs)
    return eng, sessionmaker(bind=eng, expire_on_commit=False)


# ---------------------------------------------------------------------
# 3. BLOCKING  •  PostgreSQL  (psycopg2)
# ---------------------------------------------------------------------
def blocking_postgres_engine(
    dsn: str | None = None,
    user: str = "app",
    pwd: str | None = None,
    host: str = "localhost",
    port: int = 5432,
    db: str = "app_db",
    pool_size: int = 10,
    max_overflow: int = 20,
):
    if dsn:
        url = dsn
    else:
        user = os.getenv("PGUSER", user)
        pwd = os.getenv("PGPASSWORD", pwd or "secret")
        host = os.getenv("PGHOST", host)
        port = int(os.getenv("PGPORT", port))
        db = os.getenv("PGDATABASE", db)
        url = f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"
    eng = create_engine(
        url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=True,  # drops stale connections
        echo=False,
        future=True,
    )
    return eng, sessionmaker(bind=eng, expire_on_commit=False)


# ───────────────────────────────────────────────────────────────────────
# HybridSession: async under the hood, classic Session façade on top
# ───────────────────────────────────────────────────────────────────────
class HybridSession(AsyncSession):
    """
    An AsyncSession that ALSO behaves like a synchronous Session for the
    handful of blocking helpers AutoAPI’s CRUD cores expect (`query`,
    `commit`, `flush`, `refresh`, `get`, `delete`).
    """

    # ---- synchronous wrappers (delegate to the sync mirror) ------------
    # NOTE: self.sync_session is provided by SQLAlchemy ≥1.4
    def query(self, *e, **k):
        return self.sync_session.query(*e, **k)

    def add(self, *a, **k):
        return self.sync_session.add(*a, **k)

    async def get(self, *a, **k):
        return await super().get(*a, **k)

    async def flush(self, *a, **k):
        return await super().flush(*a, **k)

    async def commit(self, *a, **k):
        return await super().commit(*a, **k)

    async def refresh(self, *a, **k):
        return await super().refresh(*a, **k)

    async def delete(self, *a, **k):
        return await super().delete(*a, **k)

    # ---- DDL helper used at AutoAPI bootstrap --------------------------
    async def run_sync(self, fn, *a, **kw):
        try:
            return await super().run_sync(fn, *a, **kw)
        except (OSError, SQLAlchemyError) as exc:
            url = getattr(self.bind, "url", "unknown")
            await self.bind.dispose()
            raise RuntimeError(
                f"Failed to connect to database at '{url}'. "
                "Ensure the database is reachable and credentials are correct."
            ) from exc


# ----------------------------------------------------------------------
# 2. ASYNC  •  SQLite  (aiosqlite driver)
# ----------------------------------------------------------------------
def async_sqlite_engine(path: str | None = None):
    url = "sqlite+aiosqlite://" + (f"/{path}" if path else "")
    eng = create_async_engine(
        url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    return eng, async_sessionmaker(
        eng,
        expire_on_commit=False,
        class_=HybridSession,  # CHANGED ←
    )


# ----------------------------------------------------------------------
# 4. ASYNC  •  PostgreSQL  (asyncpg)
# ----------------------------------------------------------------------
def async_postgres_engine(
    dsn: str | None = None,
    user: str = "app",
    pwd: str | None = None,
    host: str = "localhost",
    port: int = 5432,
    db: str = "app_db",
    pool_size: int = 10,
    max_size: int = 20,
):
    if dsn:
        url = dsn
    else:
        user = os.getenv("PGUSER", user)
        pwd = os.getenv("PGPASSWORD", pwd or "secret")
        host = os.getenv("PGHOST", host)
        port = int(os.getenv("PGPORT", port))
        db = os.getenv("PGDATABASE", db)
        url = f"postgresql+asyncpg://{user}:{pwd}@{host}:{port}/{db}"
    eng = create_async_engine(
        url,
        pool_size=pool_size,
        max_overflow=max_size - pool_size,
        pool_pre_ping=True,
        echo=False,
    )
    return eng, async_sessionmaker(
        eng,
        expire_on_commit=False,
        class_=HybridSession,  # CHANGED ←
    )
