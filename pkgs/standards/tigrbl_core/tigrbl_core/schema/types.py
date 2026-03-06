from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal, Type, Union

try:  # pragma: no cover
    from pydantic import BaseModel  # type: ignore
except Exception:  # pragma: no cover

    class BaseModel:  # minimal typing stub
        pass


SchemaKind = Literal["in", "out"]


@dataclass(frozen=True, slots=True)
class SchemaRef:
    """Lazy reference to ``model.schemas.<alias>.(in_|out)``."""

    alias: str
    kind: SchemaKind = "in"


SchemaArg = Union[
    Type[BaseModel],
    SchemaRef,
    str,
    Callable[[type], Type[BaseModel]],
]


__all__ = ["SchemaKind", "SchemaRef", "SchemaArg"]
