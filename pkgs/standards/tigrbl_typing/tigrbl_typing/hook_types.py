from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Literal

HookPhase = Literal[
    "PRE_INGRESS",
    "POST_INGRESS",
    "PRE_HANDLER",
    "POST_HANDLER",
    "PRE_EGRESS",
    "POST_EGRESS",
]

Ctx = Any
StepFn = Callable[[Ctx], Awaitable[Any] | Any]
HookPredicate = Callable[[Any], bool]

__all__ = ["HookPhase", "Ctx", "StepFn", "HookPredicate"]
