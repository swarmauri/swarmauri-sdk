"""
auth_authn_idp.db
=================
Centralised SQLAlchemy 2.0 async engine / session factory.

Usage (FastAPI)
---------------
    from fastapi import Depends, APIRouter
    from auth_authn_idp.db import get_session

    router = APIRouter()

    @router.get("/tenants")
    async def list_tenants(db: AsyncSession = Depends(get_session)):
        result = await db.execute(select(Tenant))
        return result.scalars().all()
"""

from __future__ import annotations

import contextlib
import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from .config import settings

__all__ = ["engine", "AsyncSessionMaker", "get_session", "lifespan"]

log = logging.getLogger("auth_authn.db")


# --------------------------------------------------------------------------- #
# Engine singleton                                                            #
# --------------------------------------------------------------------------- #
def _create_engine() -> AsyncEngine:
    """
    Create a *singleton* SQLAlchemy AsyncEngine based on ENV configuration.

    - Uses `NullPool` for SQLite to avoid 'database is locked' in local dev.
    - Enables `pool_pre_ping` for Postgres to drop stale connections.
    """
    url = settings.database_url
    echo = settings.log_level.upper() == "DEBUG"

    if url.startswith("sqlite"):
        return create_async_engine(
            url,
            echo=echo,
            poolclass=NullPool,
            connect_args={"check_same_thread": False},
        )

    # Postgres / others
    return create_async_engine(
        url,
        echo=echo,
        pool_pre_ping=True,
        pool_size=20,
        max_overflow=10,
    )


engine: AsyncEngine | None = None  # initialised lazily during lifespan


# --------------------------------------------------------------------------- #
# Session factory                                                             #
# --------------------------------------------------------------------------- #
AsyncSessionMaker: async_sessionmaker[AsyncSession] | None = None


def _initialise_sessionmaker() -> None:
    global AsyncSessionMaker
    if AsyncSessionMaker is None:
        AsyncSessionMaker = async_sessionmaker(
            engine, expire_on_commit=False, autoflush=False, autocommit=False
        )


# --------------------------------------------------------------------------- #
# FastAPI‑style lifespan helper (optional)                                    #
# --------------------------------------------------------------------------- #
@contextlib.asynccontextmanager
async def lifespan(app):  # type: ignore[valid-type]
    """
    Call this in `main.py`:

        app = FastAPI(lifespan=lifespan)
    """
    global engine
    engine = _create_engine()
    _initialise_sessionmaker()
    log.info("🔗  DB engine created (url=%s)", settings.database_url)

    try:
        yield
    finally:
        if engine:
            await engine.dispose()
            log.info("🔌  DB engine disposed")


# --------------------------------------------------------------------------- #
# Session dependency                                                          #
# --------------------------------------------------------------------------- #
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an `AsyncSession`.

    Example:
        from fastapi import Depends
        from auth_authn_idp.db import get_session

        @router.post("/users")
        async def create_user(payload: UserIn, db: AsyncSession = Depends(get_session)):
            db.add(User(**payload.model_dump()))
            await db.commit()
    """
    if AsyncSessionMaker is None:  # pragma: no cover
        # Called outside an ASGI lifespan (e.g. CLI)
        global engine
        if engine is None:
            engine = _create_engine()
            _initialise_sessionmaker()

    async with AsyncSessionMaker() as session:  # type: ignore[arg-type]
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        else:
            # Commit only if caller didn't explicitly commit/rollback
            if session.in_transaction():
                await session.commit()
