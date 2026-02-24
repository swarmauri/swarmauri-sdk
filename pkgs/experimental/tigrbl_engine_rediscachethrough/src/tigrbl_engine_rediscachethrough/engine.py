from __future__ import annotations
from typing import Any, Callable, Tuple

from redis import Redis
from tigrbl.engine.builders import blocking_postgres_engine
from .session import CacheThroughSession


def rediscachethrough_engine(
    dsn: str | None = None,
    user: str = "app",
    pwd: str | None = None,
    host: str = "localhost",
    port: int = 5432,
    db: str = "app_db",
    redis_url: str = "redis://localhost:6379/0",
    cache_ttl_sec: int = 60,
    **kwargs: Any,
) -> Tuple[Any, Callable[[], Any]]:
    """Build the underlying Postgres + Redis handles and return a session factory.

    Returns:
        engine_handles: dict with 'pg_engine', 'sessionmaker', 'redis'
        session_factory: () -> CacheThroughSession
    """
    # Reuse tigrbl's canonical Postgres builder
    pg_engine, sessionmaker = blocking_postgres_engine(
        dsn=dsn, user=user, pwd=pwd, host=host, port=port, db=db
    )
    r = Redis.from_url(redis_url, decode_responses=False)

    def session_factory() -> CacheThroughSession:
        sa_sess = sessionmaker()  # SQLAlchemy Session (sync)
        return CacheThroughSession(
            sa_session=sa_sess,
            redis_client=r,
            cache_ttl_sec=cache_ttl_sec,
        )

    engine_handles = {
        "pg_engine": pg_engine,
        "sessionmaker": sessionmaker,
        "redis": r,
    }
    return engine_handles, session_factory


def rediscachethrough_capabilities() -> dict:
    return {
        "sql": True,
        "dataframe": False,
        "transactions": True,
        "distributed": False,
        "cache": "read-through/write-through",
        "dialect": "postgresql+sqlalchemy",
    }
