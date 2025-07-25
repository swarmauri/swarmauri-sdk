# ─────────────── schema registry helper ────────────────
from functools import lru_cache
from typing import Literal, TypeAlias, Any
from pydantic import BaseModel, Field, create_model, ConfigDict

_SchemaTag: TypeAlias = Literal["create", "read", "update", "delete", "list"]


@lru_cache(maxsize=None)
def get_autoapi_schema(
    orm_cls: type,
    tag: _SchemaTag,
) -> type[BaseModel]:
    """
    >>> SCreate = get_autoapi_schema(User, "create")
    >>> SListIn = get_autoapi_schema(User, "list")
    The return value is *exactly* the model class AutoAPI generates
    internally, so you can use it for type-hints or client generation.
    """
    from . import AutoAPI

    # -- define the four core variants ---------------------------------
    def _schema(verb: str):
        return AutoAPI._schema(orm_cls, verb=verb)

    SRead = _schema("read")
    SCreate = _schema("create")
    SUpdate = _schema("update")
    SDelete = _schema("delete")

    def _make_list():
        base = dict(skip=(int, Field(0, ge=0)), limit=(int | None, Field(None, ge=1)))
        opts = {c.name: (Any | None, Field(None)) for c in orm_cls.__table__.columns}
        return create_model(
            f"{orm_cls.__name__}ListParams",
            __config__=ConfigDict(extra="forbid"),
            **base,
            **opts,
        )

    SListIn = _make_list()

    mapping: dict[_SchemaTag, type[BaseModel]] = {
        "create": SCreate,
        "read": SRead,
        "update": SUpdate,
        "delete": SDelete,
        "list": SListIn,
    }
    return mapping[tag]
