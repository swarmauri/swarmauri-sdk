"""Parameter marker helpers for stdapi dependency resolution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Param:
    default: Any = None
    alias: str | None = None
    required: bool = False
    location: str = "query"


def Body(default: Any = None, **kwargs: Any) -> Param:
    return Param(
        default=default,
        alias=kwargs.get("alias"),
        required=default is ...,
        location="body",
    )


def Query(default: Any = None, **kwargs: Any) -> Param:
    return Param(
        default=default,
        alias=kwargs.get("alias"),
        required=default is ...,
        location="query",
    )


def Path(default: Any = None, **kwargs: Any) -> Param:
    return Param(
        default=default,
        alias=kwargs.get("alias"),
        required=default is ...,
        location="path",
    )


def Header(default: Any = None, **kwargs: Any) -> Param:
    return Param(
        default=default,
        alias=kwargs.get("alias"),
        required=default is ...,
        location="header",
    )
