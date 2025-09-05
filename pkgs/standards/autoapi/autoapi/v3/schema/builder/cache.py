"""Cache and type definitions for schema builder."""

from __future__ import annotations

from typing import Dict, Tuple, Type, Union, Literal

from pydantic import BaseModel

_SchemaVerb = Union[
    Literal["create"],
    Literal["read"],
    Literal["update"],
    Literal["replace"],
    Literal["merge"],
    Literal["delete"],
    Literal["list"],
    Literal["clear"],
]

_SchemaCache: Dict[
    Tuple[type, str, frozenset, frozenset, str | None], Type[BaseModel]
] = {}

__all__ = ["_SchemaVerb", "_SchemaCache"]
