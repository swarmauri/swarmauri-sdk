from __future__ import annotations

from typing import Any, Sequence, Type

from .router_spec import RouterSpec
from ._router import Router


def defineRouterSpec(
    *,
    name: str = "router",
    prefix: str = "",
    tags: Sequence[str] = (),
    engine: Any = None,
    ops: Sequence[Any] = (),
    schemas: Sequence[Any] = (),
    hooks: Sequence[Any] = (),
    security_deps: Sequence[Any] = (),
    deps: Sequence[Any] = (),
    models: Sequence[Any] = (),
) -> Type[RouterSpec]:
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


def deriveRouter(**kw: Any) -> Type[Router]:
    spec = defineRouterSpec(**kw)
    return type("RouterWithSpec", (spec, Router), {})


__all__ = ["defineRouterSpec", "deriveRouter"]
