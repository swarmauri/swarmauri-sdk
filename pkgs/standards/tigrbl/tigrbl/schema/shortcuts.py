# tigrbl/v3/schema/shortcuts.py
from __future__ import annotations

from typing import Optional, Type

try:  # pragma: no cover
    from pydantic import BaseModel  # type: ignore
except Exception:  # pragma: no cover

    class BaseModel:  # minimal stub for typing only
        pass


from ._schema import Schema
from .schema_spec import SchemaSpec
from .types import SchemaArg, SchemaKind


def schema_spec(
    alias: str,
    *,
    kind: SchemaKind = "out",
    for_: Optional[type] = None,
    schema: SchemaArg | None = None,
) -> SchemaSpec:
    """Factory for :class:`SchemaSpec`."""

    return SchemaSpec(alias=alias, kind=kind, for_=for_, schema=schema)


def schema(
    model: Type[BaseModel],
    *,
    kind: SchemaKind = "out",
    alias: str | None = None,
) -> Schema:
    """Factory for :class:`Schema`."""

    return Schema(model=model, kind=kind, alias=alias)


__all__ = ["schema_spec", "schema"]
