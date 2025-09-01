# autoapi/autoapi/v3/api/shortcuts.py
from __future__ import annotations

from typing import Any, Sequence, Type

from .api_spec import APISpec
from ._api import Api


def defineApiSpec(
    *,
    # identity
    name: str = "api",
    prefix: str = "",
    tags: Sequence[str] = (),
    # engine
    db: Any = None,
    # composition
    ops: Sequence[Any] = (),
    schemas: Sequence[Any] = (),
    hooks: Sequence[Any] = (),
    security_deps: Sequence[Any] = (),
    deps: Sequence[Any] = (),
    models: Sequence[Any] = (),
) -> Type[APISpec]:
    """
    Build an API spec class with class attributes only (no instances).
    Use it directly in your class MRO:

        class TenantA(defineApiSpec(name="tenantA", db=...)):
            pass

    or pass it to ``deriveApi(...)`` to get a concrete :class:`Api` subclass.
    """
    attrs = dict(
        NAME=name,
        PREFIX=prefix,
        TAGS=tuple(tags or ()),
        DB=db,
        OPS=tuple(ops or ()),
        SCHEMAS=tuple(schemas or ()),
        HOOKS=tuple(hooks or ()),
        SECURITY_DEPS=tuple(security_deps or ()),
        DEPS=tuple(deps or ()),
        MODELS=tuple(models or ()),
    )
    return type("APISpec", (APISpec,), attrs)


def deriveApi(**kw: Any) -> Type[Api]:
    """Produce a concrete :class:`Api` subclass that inherits the spec."""
    Spec = defineApiSpec(**kw)
    return type("APIWithSpec", (Spec, Api), {})


__all__ = ["defineApiSpec", "deriveApi"]
