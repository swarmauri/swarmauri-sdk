# tigrbl/v3/schema/types.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Type, Union, Literal

try:  # pragma: no cover
    from pydantic import BaseModel  # type: ignore
except Exception:  # pragma: no cover

    class BaseModel:  # minimal stub for typing only
        pass


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


__all__ = ["SchemaKind", "SchemaRef", "SchemaArg"]
