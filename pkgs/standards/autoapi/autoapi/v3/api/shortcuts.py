# autoapi/autoapi/v3/api/shortcuts.py
from __future__ import annotations

from typing import Any, Sequence, Type

from .api_spec import APISpecMixin
from ._api import API


def apiS(
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
) -> Type[APISpecMixin]:
    """
    Build an API-spec *mixin* class with class attributes only (no instances).
    Use it directly in your class MRO:

        class TenantA(apiS(name="tenantA", db=...)):
            pass

    or pass it to `api(...)` to get a concrete API subclass.
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
    return type("APISpec", (APISpecMixin,), attrs)


def api(**kw: Any) -> Type[API]:
    """
    Produce a concrete API subclass that *inherits* the spec mixin.
    Example:

        TenantA = api(name="tenantA", prefix="/tA", db="sqlite:///./tenantA.sqlite",
                      models=(User, Task))
        tenant_a = TenantA()
    """
    Spec = apiS(**kw)
    return type("APIWithSpec", (Spec, API), {})


__all__ = ["apiS", "api"]
