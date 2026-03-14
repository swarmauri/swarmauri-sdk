# tigrbl/tigrbl/v3/app/shortcuts.py
from __future__ import annotations

from typing import Any, Sequence, Type

from .._spec.app_spec import AppSpec
from .._concrete.tigrbl_app import TigrblApp


def defineAppSpec(
    *,
    title: str = "Tigrbl",
    version: str = "0.1.0",
    engine: Any = None,
    # composition
    routers: Sequence[Any] = (),
    ops: Sequence[Any] = (),
    tables: Sequence[Any] = (),
    schemas: Sequence[Any] = (),
    hooks: Sequence[Any] = (),
    # deps & security
    security_deps: Sequence[Any] = (),
    deps: Sequence[Any] = (),
    # prefixes
    jsonrpc_prefix: str = "/rpc",
    system_prefix: str = "/system",
    # framework bits
    middlewares: Sequence[Any] = (),
    lifespan: Any = None,
) -> Type[AppSpec]:
    """
    Build an App-spec class with class attributes only (no instances).
    Use it directly in your class MRO:

        class MyApp(defineAppSpec(title="Svc", engine=...)):
            pass

    or pass it to `deriveApp(...)` to get a concrete App subclass.
    """
    attrs = dict(
        TITLE=title,
        VERSION=version,
        ENGINE=engine,
        ROUTERS=tuple(routers or ()),
        OPS=tuple(ops or ()),
        TABLES=tuple(tables or ()),
        SCHEMAS=tuple(schemas or ()),
        HOOKS=tuple(hooks or ()),
        SECURITY_DEPS=tuple(security_deps or ()),
        DEPS=tuple(deps or ()),
        JSONRPC_PREFIX=jsonrpc_prefix,
        SYSTEM_PREFIX=system_prefix,
        MIDDLEWARES=tuple(middlewares or ()),
        LIFESPAN=lifespan,
    )
    return type("AppSpec", (AppSpec,), attrs)


def deriveApp(**kw: Any) -> Type[TigrblApp]:
    """Produce a concrete :class:`TigrblApp` subclass that inherits the spec."""
    Spec = defineAppSpec(**kw)
    forwarded = {
        "TITLE": getattr(Spec, "TITLE", "Tigrbl"),
        "VERSION": getattr(Spec, "VERSION", "0.1.0"),
        "ENGINE": getattr(Spec, "ENGINE", None),
        "ROUTERS": tuple(getattr(Spec, "ROUTERS", ()) or ()),
        "OPS": tuple(getattr(Spec, "OPS", ()) or ()),
        "TABLES": tuple(getattr(Spec, "TABLES", ()) or ()),
        "SCHEMAS": tuple(getattr(Spec, "SCHEMAS", ()) or ()),
        "HOOKS": tuple(getattr(Spec, "HOOKS", ()) or ()),
        "SECURITY_DEPS": tuple(getattr(Spec, "SECURITY_DEPS", ()) or ()),
        "DEPS": tuple(getattr(Spec, "DEPS", ()) or ()),
        "JSONRPC_PREFIX": getattr(Spec, "JSONRPC_PREFIX", "/rpc"),
        "SYSTEM_PREFIX": getattr(Spec, "SYSTEM_PREFIX", "/system"),
        "MIDDLEWARES": tuple(getattr(Spec, "MIDDLEWARES", ()) or ()),
        "LIFESPAN": getattr(Spec, "LIFESPAN", None),
    }
    return type("AppWithSpec", (TigrblApp, Spec), forwarded)


__all__ = ["defineAppSpec", "deriveApp"]
