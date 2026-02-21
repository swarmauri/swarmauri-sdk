# tigrbl/tigrbl/v3/api/shortcuts.py
from __future__ import annotations

from typing import Any, Sequence, Type

from .router_spec import RouterSpec
from ._api import Api


def defineRouterSpec(
    *,
    # identity
    name: str = "api",
    prefix: str = "",
    tags: Sequence[str] = (),
    # engine
    engine: Any = None,
    # composition
    ops: Sequence[Any] = (),
    schemas: Sequence[Any] = (),
    hooks: Sequence[Any] = (),
    security_deps: Sequence[Any] = (),
    deps: Sequence[Any] = (),
    models: Sequence[Any] = (),
) -> Type[RouterSpec]:
    """
    Build an API-spec class with class attributes only (no instances).
    Use it directly in your class MRO:

        class TenantA(defineRouterSpec(name="tenantA", engine=...)):
            pass

    or pass it to `deriveRouter(...)` to get a concrete API subclass.
    """
    attrs = dict(
        NAME=name,
        PREFIX=prefix,
        TAGS=tuple(tags or ()),
        ENGINE=engine,
        OPS=tuple(ops or ()),
        SCHEMAS=tuple(schemas or ()),
        HOOKS=tuple(hooks or ()),
        SECURITY_DEPS=tuple(security_deps or ()),
        DEPS=tuple(deps or ()),
        MODELS=tuple(models or ()),
    )
    return type("RouterSpec", (RouterSpec,), attrs)


def deriveRouter(**kw: Any) -> Type[Api]:
    """Produce a concrete :class:`Api` subclass that inherits the spec."""
    Spec = defineRouterSpec(**kw)
    return type("APIWithSpec", (Spec, Api), {})


__all__ = ["defineRouterSpec", "deriveRouter", "defineApiSpec", "deriveApi"]


# Backward-compatible aliases
defineApiSpec = defineRouterSpec
deriveApi = deriveRouter
