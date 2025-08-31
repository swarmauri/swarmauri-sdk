# autoapi/autoapi/v3/api/api_spec.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Sequence
from ..engine.engine_spec import EngineCtx


@dataclass
class APISpec:
    """
    Used to *produce an API subclass* via API.from_spec().
    """

    name: str = "api"
    prefix: str = ""
    db: Optional[EngineCtx] = None
    tags: Sequence[str] = field(default_factory=tuple)

    # NEW
    ops: Sequence[Any] = field(default_factory=tuple)
    schemas: Sequence[Any] = field(default_factory=tuple)
    hooks: Sequence[Callable[..., Any]] = field(default_factory=tuple)
    security_deps: Sequence[Callable[..., Any]] = field(default_factory=tuple)
    deps: Sequence[Callable[..., Any]] = field(default_factory=tuple)

    # optional: models this API exposes (auto-install)
    models: Sequence[Any] = field(default_factory=tuple)
