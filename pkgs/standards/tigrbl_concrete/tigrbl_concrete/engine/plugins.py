"""Concrete engine registrations for tigrbl-core EngineSpec."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tigrbl_core._spec.registry import register_engine

from .builders import (
    async_postgres_engine,
    async_sqlite_engine,
    blocking_postgres_engine,
    blocking_sqlite_engine,
)


@dataclass(frozen=True)
class _SQLiteRegistration:
    def build(self, *, mapping: dict[str, object], spec: Any, dsn: str | None):
        if spec.async_:
            return async_sqlite_engine(path=spec.path, pool=spec.pool)
        return blocking_sqlite_engine(path=spec.path, pool=spec.pool)

    def capabilities(
        self, *, spec: Any, mapping: dict[str, object] | None = None
    ) -> dict[str, Any]:
        return {
            "transactional": True,
            "async_native": bool(spec.async_),
            "isolation_levels": {"SERIALIZABLE", "READ UNCOMMITTED"},
            "read_only_enforced": False,
            "engine": "sqlite",
        }


@dataclass(frozen=True)
class _PostgresRegistration:
    def build(self, *, mapping: dict[str, object], spec: Any, dsn: str | None):
        if spec.async_:
            return async_postgres_engine(
                dsn=dsn or spec.dsn,
                user=spec.user or "app",
                pwd=spec.pwd,
                host=spec.host or "localhost",
                port=spec.port or 5432,
                db=spec.name or "app_db",
                pool_size=spec.pool_size,
                max_size=spec.max,
            )
        return blocking_postgres_engine(
            dsn=dsn or spec.dsn,
            user=spec.user or "app",
            pwd=spec.pwd,
            host=spec.host or "localhost",
            port=spec.port or 5432,
            db=spec.name or "app_db",
            pool_size=spec.pool_size,
            max_overflow=spec.max,
        )

    def capabilities(
        self, *, spec: Any, mapping: dict[str, object] | None = None
    ) -> dict[str, Any]:
        return {
            "transactional": True,
            "async_native": bool(spec.async_),
            "isolation_levels": {
                "READ UNCOMMITTED",
                "READ COMMITTED",
                "REPEATABLE READ",
                "SERIALIZABLE",
            },
            "read_only_enforced": True,
            "engine": "postgres",
        }


def register() -> None:
    """Register concrete sqlite/postgres providers in the core registry."""
    register_engine("sqlite", _SQLiteRegistration())
    register_engine("postgres", _PostgresRegistration())
