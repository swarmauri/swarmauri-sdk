# pkgs/standards/tigrbl_core/tigrbl/_spec/schema_spec.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal, Optional, Type, Union

try:  # pragma: no cover
    from pydantic import BaseModel  # type: ignore
except Exception:  # pragma: no cover

    class BaseModel:  # minimal stub for typing only
        pass


from .serde import SerdeMixin


SchemaKind = Literal["in", "out"]


@dataclass(frozen=True, slots=True)
class SchemaRef:
    """Lazy reference to ``model.schemas.<alias>.(in_|out)``."""

    alias: str
    kind: SchemaKind = "in"


SchemaArg = Union[
    Type[BaseModel],  # direct Pydantic model
    SchemaRef,  # cross-op reference
    str,  # "alias.in" | "alias.out"
    Callable[[type], Type[BaseModel]],  # lambda cls: cls.schemas.create.in_
]


@dataclass(frozen=True, slots=True)
class SchemaSpec(SerdeMixin):
    """Declarative description of a schema for a model."""

    alias: str
    kind: SchemaKind = "out"
    for_: Optional[type] = None
    schema: SchemaArg | None = None


__all__ = ["SchemaKind", "SchemaRef", "SchemaArg", "SchemaSpec"]
