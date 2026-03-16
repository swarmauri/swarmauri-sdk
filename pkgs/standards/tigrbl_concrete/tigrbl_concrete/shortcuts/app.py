from __future__ import annotations

from typing import Any, Sequence, Type

from tigrbl_core._spec.app_spec import AppSpec
from tigrbl_concrete._concrete.tigrbl_app import TigrblApp


def defineAppSpec(
    *,
    title: str = "Tigrbl",
    version: str = "0.1.0",
    engine: Any = None,
    routers: Sequence[Any] = (),
    ops: Sequence[Any] = (),
    tables: Sequence[Any] = (),
    schemas: Sequence[Any] = (),
    hooks: Sequence[Any] = (),
    security_deps: Sequence[Any] = (),
    deps: Sequence[Any] = (),
    jsonrpc_prefix: str = "/rpc",
    system_prefix: str = "/system",
    middlewares: Sequence[Any] = (),
    lifespan: Any = None,
) -> Type[AppSpec]:
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
    spec = defineAppSpec(**kw)
    attrs = {
        "TITLE": getattr(spec, "TITLE", "Tigrbl"),
        "VERSION": getattr(spec, "VERSION", "0.1.0"),
        "ENGINE": getattr(spec, "ENGINE", None),
        "ROUTERS": tuple(getattr(spec, "ROUTERS", ()) or ()),
        "OPS": tuple(getattr(spec, "OPS", ()) or ()),
        "TABLES": tuple(getattr(spec, "TABLES", ()) or ()),
        "SCHEMAS": tuple(getattr(spec, "SCHEMAS", ()) or ()),
        "HOOKS": tuple(getattr(spec, "HOOKS", ()) or ()),
        "SECURITY_DEPS": tuple(getattr(spec, "SECURITY_DEPS", ()) or ()),
        "DEPS": tuple(getattr(spec, "DEPS", ()) or ()),
        "JSONRPC_PREFIX": getattr(spec, "JSONRPC_PREFIX", "/rpc"),
        "SYSTEM_PREFIX": getattr(spec, "SYSTEM_PREFIX", "/system"),
        "MIDDLEWARES": tuple(getattr(spec, "MIDDLEWARES", ()) or ()),
        "LIFESPAN": getattr(spec, "LIFESPAN", None),
    }
    return type("AppWithSpec", (TigrblApp, spec), attrs)


__all__ = ["defineAppSpec", "deriveApp"]
