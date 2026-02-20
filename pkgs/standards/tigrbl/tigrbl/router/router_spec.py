from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Sequence

from ..engine.engine_spec import EngineCfg
from ..responses.types import ResponseSpec


@dataclass
class RouterSpec:
    """Used to produce a router subclass via Router.from_spec()."""

    name: str = "router"
    prefix: str = ""
    engine: Optional[EngineCfg] = None
    tags: Sequence[str] = field(default_factory=tuple)
    ops: Sequence[Any] = field(default_factory=tuple)
    schemas: Sequence[Any] = field(default_factory=tuple)
    hooks: Sequence[Callable[..., Any]] = field(default_factory=tuple)
    security_deps: Sequence[Callable[..., Any]] = field(default_factory=tuple)
    deps: Sequence[Callable[..., Any]] = field(default_factory=tuple)
    response: Optional[ResponseSpec] = None
    models: Sequence[Any] = field(default_factory=tuple)
