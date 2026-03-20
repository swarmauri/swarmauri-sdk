"""Engine utilities for collecting and binding database providers."""

from __future__ import annotations

from tigrbl_concrete._concrete._engine import Engine
from tigrbl_concrete.engine.builders import (
    HybridSession,
    async_postgres_engine,
    async_sqlite_engine,
    blocking_postgres_engine,
    blocking_sqlite_engine,
)
from tigrbl_concrete.engine.collect import collect_engine_config
from tigrbl_concrete.engine.plugins import (
    load_engine_plugins as _bootstrap_load_engine_plugins,
)


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
    from tigrbl_concrete.engine.bind import collect as _collect

    return _collect(*args, **kwargs)


def install(*args, **kwargs):
    from tigrbl_concrete.engine.bind import install as _install

    return _install(*args, **kwargs)


def bind(*args, **kwargs):
    from tigrbl_concrete.engine.bind import bind as _bind

    return _bind(*args, **kwargs)


def install_from_objects(*args, **kwargs):
    from tigrbl_concrete.engine.bind import (
        install_from_objects as _install_from_objects,
    )

    return _install_from_objects(*args, **kwargs)


def load_engine_plugins(*args, **kwargs):
    from tigrbl_concrete.engine.plugins import (
        load_engine_plugins as _load_engine_plugins,
    )

    return _load_engine_plugins(*args, **kwargs)


def register_engine(*args, **kwargs):
    from tigrbl_concrete.engine.registry import register_engine as _register_engine

    return _register_engine(*args, **kwargs)


def known_engine_kinds(*args, **kwargs):
    from tigrbl_concrete.engine.registry import (
        known_engine_kinds as _known_engine_kinds,
    )

    return _known_engine_kinds(*args, **kwargs)


def get_engine_registration(*args, **kwargs):
    from tigrbl_concrete.engine.registry import (
        get_engine_registration as _get_engine_registration,
    )

    return _get_engine_registration(*args, **kwargs)


try:
    _bootstrap_load_engine_plugins()
except Exception:
    pass


def engine(*args, **kwargs):
    from tigrbl_core._spec.engine_spec import EngineSpec

    if args:
        spec = args[0]
    elif kwargs:
        spec = kwargs
    else:
        spec = None
    if isinstance(spec, EngineSpec):
        return Engine(spec)
    return Engine(EngineSpec.from_any(spec))


def _register_concrete_defaults() -> None:
    """Register built-in concrete engine kinds in the shared core registry."""
    from tigrbl_core._spec.registry import register_engine

    class _SQLiteRegistration:
        def build(self, *, mapping, spec, dsn):
            if spec.async_:
                return async_sqlite_engine(path=spec.path, pool=spec.pool)
            return blocking_sqlite_engine(path=spec.path, pool=spec.pool)

        def capabilities(self, *, spec, mapping=None):
            return {
                "transactional": True,
                "async_native": bool(spec.async_),
                "isolation_levels": {"SERIALIZABLE", "READ UNCOMMITTED"},
                "read_only_enforced": False,
                "engine": "sqlite",
            }

    class _PostgresRegistration:
        def build(self, *, mapping, spec, dsn):
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

        def capabilities(self, *, spec, mapping=None):
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

    register_engine("sqlite", _SQLiteRegistration())
    register_engine("postgres", _PostgresRegistration())


def __getattr__(name: str):
    if name == "resolver":
        from tigrbl_concrete._concrete import engine_resolver as resolver

        return resolver
    if name == "EngineSpec":
        from tigrbl_core._spec.engine_spec import EngineSpec

        return EngineSpec
    raise AttributeError(name)
