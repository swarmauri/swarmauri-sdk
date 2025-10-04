"""Engine utilities for collecting and binding database providers."""

from .bind import bind, install_from_objects
from .collect import collect_engine_config
from .builders import (
    async_postgres_engine,
    async_sqlite_engine,
    blocking_postgres_engine,
    blocking_sqlite_engine,
    HybridSession,
)
from ._engine import Engine
from .shortcuts import engine

__all__ = [
    "collect_engine_config",
    "bind",
    "install_from_objects",
    "blocking_sqlite_engine",
    "blocking_postgres_engine",
    "async_sqlite_engine",
    "async_postgres_engine",
    "HybridSession",
    "Engine",
    "engine",
]


# Optional engine plugin support
from .plugins import load_engine_plugins
from .registry import register_engine, known_engine_kinds, get_engine_registration

# Load external engines automatically on import (idempotent)
try:
    load_engine_plugins()
except Exception:
    # Import-time plugin load should never fail the package import
    pass

__all__ += [
    "load_engine_plugins",
    "register_engine",
    "known_engine_kinds",
    "get_engine_registration",
]
