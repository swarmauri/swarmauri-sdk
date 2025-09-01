# autoapi/autoapi/v3/app/shortcuts.py
from __future__ import annotations

from typing import Any, Sequence, Type

from .app_spec import AppSpecMixin
from ._app import App


def defineAppSpec(
    *,
    title: str = "AutoAPI",
    version: str = "0.1.0",
    db: Any = None,
    # composition
    apis: Sequence[Any] = (),
    ops: Sequence[Any] = (),
    models: Sequence[Any] = (),
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
) -> Type[AppSpecMixin]:
    """
    Build an App-spec *mixin* class with class attributes only (no instances).
    Use it directly in your class MRO:

        class MyApp(defineAppSpec(title="Svc", db=...)):
            pass

    or pass it to `deriveApp(...)` to get a concrete App subclass.
    """
    attrs = dict(
        TITLE=title,
        VERSION=version,
        DB=db,
        APIS=tuple(apis or ()),
        OPS=tuple(ops or ()),
        MODELS=tuple(models or ()),
        SCHEMAS=tuple(schemas or ()),
        HOOKS=tuple(hooks or ()),
        SECURITY_DEPS=tuple(security_deps or ()),
        DEPS=tuple(deps or ()),
        JSONRPC_PREFIX=jsonrpc_prefix,
        SYSTEM_PREFIX=system_prefix,
        MIDDLEWARES=tuple(middlewares or ()),
        LIFESPAN=lifespan,
    )
    return type("AppSpec", (AppSpecMixin,), attrs)


def deriveApp(**kw: Any) -> Type[App]:
    """Produce a concrete :class:`App` subclass that inherits the spec mixin."""
    Spec = defineAppSpec(**kw)
    return type("AppWithSpec", (Spec, App), {})


__all__ = ["defineAppSpec", "deriveApp"]
