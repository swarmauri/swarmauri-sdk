"""Engine utilities for collecting and binding database providers."""

from __future__ import annotations

from .._concrete._engine import Engine
from .builders import (
    HybridSession,
    async_postgres_engine,
    async_sqlite_engine,
    blocking_postgres_engine,
    blocking_sqlite_engine,
)
from .collect import collect_engine_config
from .plugins import load_engine_plugins as _bootstrap_load_engine_plugins


__all__ = [
    "collect_engine_config",
    "collect",
    "install",
    "bind",
    "install_from_objects",
    "resolver",
    "blocking_sqlite_engine",
    "blocking_postgres_engine",
    "async_sqlite_engine",
    "async_postgres_engine",
    "HybridSession",
    "Engine",
    "EngineSpec",
    "engine",
    "load_engine_plugins",
    "register_engine",
    "known_engine_kinds",
    "get_engine_registration",
]


def collect(*args, **kwargs):
    from .bind import collect as _collect

    return _collect(*args, **kwargs)


def install(*args, **kwargs):
    from .bind import install as _install

    return _install(*args, **kwargs)


def bind(*args, **kwargs):
    from .bind import bind as _bind

    return _bind(*args, **kwargs)


def install_from_objects(*args, **kwargs):
    from .bind import install_from_objects as _install_from_objects

    return _install_from_objects(*args, **kwargs)


def load_engine_plugins(*args, **kwargs):
    from .plugins import load_engine_plugins as _load_engine_plugins

    return _load_engine_plugins(*args, **kwargs)


def register_engine(*args, **kwargs):
    from .registry import register_engine as _register_engine

    return _register_engine(*args, **kwargs)


def known_engine_kinds(*args, **kwargs):
    from .registry import known_engine_kinds as _known_engine_kinds

    return _known_engine_kinds(*args, **kwargs)


def get_engine_registration(*args, **kwargs):
    from .registry import get_engine_registration as _get_engine_registration

    return _get_engine_registration(*args, **kwargs)


try:
    _bootstrap_load_engine_plugins()
except Exception:
    pass


def engine(*args, **kwargs):
    from ..shortcuts.engine import engine as _engine

    return _engine(*args, **kwargs)


def __getattr__(name: str):
    if name == "resolver":
        from tigrbl_concrete._concrete import engine_resolver as resolver

        return resolver
    if name == "EngineSpec":
        from .._spec.engine_spec import EngineSpec

        return EngineSpec
    raise AttributeError(name)
