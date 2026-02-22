# tigrbl/tigrbl/v3/router/router_spec.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Sequence
from ..engine.engine_spec import EngineCfg
from ..responses.types import ResponseSpec


@dataclass
class RouterSpec:
    """
    Used to *produce a router subclass* via Api.from_spec().
    """

    name: str = "api"
    prefix: str = ""
    engine: Optional[EngineCfg] = None
    tags: Sequence[str] = field(default_factory=tuple)

    # NEW
    ops: Sequence[Any] = field(default_factory=tuple)
    schemas: Sequence[Any] = field(default_factory=tuple)
    hooks: Sequence[Callable[..., Any]] = field(default_factory=tuple)
    security_deps: Sequence[Callable[..., Any]] = field(default_factory=tuple)
    deps: Sequence[Callable[..., Any]] = field(default_factory=tuple)

    response: Optional[ResponseSpec] = None

    # optional: models this router exposes (auto-install)
    models: Sequence[Any] = field(default_factory=tuple)
