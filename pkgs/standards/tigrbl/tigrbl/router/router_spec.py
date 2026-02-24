<<<<<<<< HEAD:pkgs/standards/tigrbl/tigrbl/router/router_spec.py
========
# tigrbl/tigrbl/v3/router/router_spec.py
>>>>>>>> master:pkgs/standards/tigrbl/tigrbl/specs/router_spec.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Sequence

from ..engine.engine_spec import EngineCfg
from ..responses.types import ResponseSpec


@dataclass
class RouterSpec:
<<<<<<<< HEAD:pkgs/standards/tigrbl/tigrbl/router/router_spec.py
    """Used to produce a router subclass via Router.from_spec()."""

    name: str = "router"
========
    """
    Used to *produce a router subclass* via Router.from_spec().
    """

    name: str = ""
>>>>>>>> master:pkgs/standards/tigrbl/tigrbl/specs/router_spec.py
    prefix: str = ""
    engine: Optional[EngineCfg] = None
    tags: Sequence[str] = field(default_factory=tuple)
    ops: Sequence[Any] = field(default_factory=tuple)
    schemas: Sequence[Any] = field(default_factory=tuple)
    hooks: Sequence[Callable[..., Any]] = field(default_factory=tuple)
    security_deps: Sequence[Callable[..., Any]] = field(default_factory=tuple)
    deps: Sequence[Callable[..., Any]] = field(default_factory=tuple)
    response: Optional[ResponseSpec] = None
<<<<<<<< HEAD:pkgs/standards/tigrbl/tigrbl/router/router_spec.py
    models: Sequence[Any] = field(default_factory=tuple)
========

    # optional: tables this router exposes (auto-install)
    tables: Sequence[Any] = field(default_factory=tuple)
>>>>>>>> master:pkgs/standards/tigrbl/tigrbl/specs/router_spec.py
