from __future__ import annotations

from tigrbl.engine.registry import register_engine

from .engine import InMemoryEngine
from .session import AsyncInMemorySession, InMemorySession


def register() -> None:
    register_engine(
        kind="inmemory",
        build=build_inmemory,
        capabilities=capabilities,
    )


def capabilities() -> dict:
    return {
        "engine": "inmemory",
        "transactional": True,
        "async_native": True,
        "isolation_levels": {"snapshot"},
        "read_only_enforced": False,
        "persistence": "process",
    }


def build_inmemory(*, mapping=None, spec=None, dsn=None, **_) -> tuple[object, object]:
    mapping = dict(mapping or {})
    async_ = bool(getattr(spec, "async_", False))
    engine = InMemoryEngine(
        namespace=str(mapping.get("namespace", "default")),
        enforce_schema=bool(mapping.get("enforce_schema", False)),
    )

    if async_:

        def sessionmaker():
            return AsyncInMemorySession(engine)
    else:

        def sessionmaker():
            return InMemorySession(engine)

    return engine, sessionmaker
