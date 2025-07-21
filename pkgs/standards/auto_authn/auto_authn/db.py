"""
auth_authn_idp.db
=================
Centralised SQLAlchemy 2.x *async* engine & session factory.

Key features
------------
• Lazy, singleton **AsyncEngine** created once per process.
• `NullPool` for SQLite (avoids “database is locked” in dev); pooled
  connections with `pool_pre_ping` for Postgres.
• FastAPI‑style `lifespan()` helper that auto‑creates / disposes the engine.
• `get_session()` dependency – automatic rollback on error, commit otherwise.
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

__all__ = ["engine", "SessionMaker", "get_session", "lifespan"]

log = logging.getLogger("auth_authn.db")

# --------------------------------------------------------------------------- #
# Engine singleton                                                            #
# --------------------------------------------------------------------------- #

engine: AsyncEngine | None = None  # instantiated lazily
SessionMaker: async_sessionmaker[AsyncSession] | None = None


def _create_engine() -> AsyncEngine:
    """
    Instantiate **one** AsyncEngine based on `settings.database_url`.
    """
    url = settings.database_url
    echo = settings.log_level.upper() == "DEBUG"

    if url.startswith("sqlite"):
        log.debug("Creating SQLite engine (url=%s)", url)
        return create_async_engine(
            url,
            echo=echo,
            poolclass=NullPool,
            connect_args={"check_same_thread": False},
        )

    # Assume PostgreSQL / other driver
    log.debug("Creating Postgres engine (url=%s)", url)
    return create_async_engine(
        url,
        echo=echo,
        pool_pre_ping=True,
        pool_size=20,
        max_overflow=10,
    )


def _init_sessionmaker() -> None:
    """Initialise global `SessionMaker`."""
    global SessionMaker
    if SessionMaker is None:  # pragma: no cover
        SessionMaker = async_sessionmaker(
            engine, expire_on_commit=False, autoflush=False, autocommit=False
        )


# --------------------------------------------------------------------------- #
# FastAPI lifespan helper                                                     #
# --------------------------------------------------------------------------- #
@contextlib.asynccontextmanager
async def lifespan(app):  # type: ignore[valid-type]
    """
    FastAPI integration:

        app = FastAPI(lifespan=lifespan)
    """
    global engine
    engine = _create_engine()
    _init_sessionmaker()
    log.info("🔗  DB engine created (url=%s)", settings.database_url)

    try:
        yield
    finally:
        if engine:
            await engine.dispose()
            log.info("🔌  DB engine disposed")


# --------------------------------------------------------------------------- #
# Dependency                                                                  #
# --------------------------------------------------------------------------- #
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an `AsyncSession`.

    Rolls back on unhandled exceptions; commits otherwise.
    """
    # If called outside ASGI context (CLI, tests), bootstrap engine/sessionmaker
    if SessionMaker is None:  # pragma: no cover
        global engine
        if engine is None:
            engine = _create_engine()
        _init_sessionmaker()

    async with SessionMaker() as session:  # type: ignore[arg-type]
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        else:
            # Commit only if caller hasn't already decided.
            if session.in_transaction():
                await session.commit()
