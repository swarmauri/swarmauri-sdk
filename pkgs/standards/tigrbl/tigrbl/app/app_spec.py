# tigrbl/tigrbl/v3/app/app_spec.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Sequence

from ..engine.engine_spec import EngineCfg
from ..response.types import ResponseSpec


@dataclass(eq=False)
class AppSpec:
    """
    Used to *produce an App subclass* via App.from_spec().
    """

    title: str = "Tigrbl"
    version: str = "0.1.0"
    engine: Optional[EngineCfg] = None

    # NEW: multi-API composition (store API classes or instances)
    apis: Sequence[Any] = field(default_factory=tuple)

    # NEW: orchestration/topology knobs
    ops: Sequence[Any] = field(default_factory=tuple)  # op descriptors or specs
    models: Sequence[Any] = field(default_factory=tuple)  # ORM classes
    schemas: Sequence[Any] = field(default_factory=tuple)  # schema classes/defs
    hooks: Sequence[Callable[..., Any]] = field(default_factory=tuple)

    # security/dep stacks (FastAPI dependencies or callables)
    security_deps: Sequence[Callable[..., Any]] = field(default_factory=tuple)
    deps: Sequence[Callable[..., Any]] = field(default_factory=tuple)

    # response defaults
    response: Optional[ResponseSpec] = None

    # system routing prefixes (REST/JSON-RPC namespaces)
    jsonrpc_prefix: str = "/rpc"
    system_prefix: str = "/system"

    # optional framework bits
    middlewares: Sequence[Any] = field(default_factory=tuple)
    lifespan: Optional[Callable[..., Any]] = None
