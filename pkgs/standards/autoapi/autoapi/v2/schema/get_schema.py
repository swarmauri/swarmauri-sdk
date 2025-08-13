# ─────────────── schema registry helper ────────────────
from functools import lru_cache
from typing import Any
from pydantic import BaseModel, Field, create_model, ConfigDict
from autoapi.v2.types import _SchemaVerb


@lru_cache(maxsize=None)
def get_autoapi_schema(
    orm_cls: type,
    op: _SchemaVerb,
) -> type[BaseModel]:
    """
    >>> SCreate = get_autoapi_schema(User, "create")
    >>> SListIn = get_autoapi_schema(User, "list")
    The return value is *exactly* the model class AutoAPI generates
    internally, so you can use it for type-hints or client generation.
    """
    from .. import AutoAPI

    # -- define the four core variants ---------------------------------
    def _schema(verb: str):
        return AutoAPI._schema(orm_cls, verb=verb)

    SRead = _schema("read")
    SCreate = _schema("create")
    SUpdate = _schema("update")
    SDelete = _schema("delete")

    tab = orm_cls.__name__

    def _make_list():
        base = dict(
            skip=(int | None, Field(None, ge=0)), limit=(int | None, Field(None, ge=1))
        )
        opts = {c.name: (Any | None, Field(None)) for c in orm_cls.__table__.columns}
        return create_model(
            f"{tab}ListParams",
            __config__=ConfigDict(extra="forbid"),
            **base,
            **opts,
        )

    SListIn = _make_list()

    mapping: dict[_SchemaVerb, type[BaseModel]] = {
        "create": SCreate,
        "read": SRead,
        "update": SUpdate,
        "delete": SDelete,
        "list": SListIn,
        # need to add clear
        # need to add support for bulk create, update, delete
    }
    return mapping[op]
