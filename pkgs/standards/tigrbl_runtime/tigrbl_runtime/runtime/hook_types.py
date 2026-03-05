"""Runtime-owned hook type definitions for Tigrbl v3."""

from __future__ import annotations

from typing import Any, Awaitable, Callable

from tigrbl_typing.phases import PHASE, HOOK_PHASES as PHASES, HookPhase

Ctx = Any
StepFn = Callable[[Ctx], Awaitable[Any] | Any]
HookPredicate = Callable[[Any], bool]

__all__ = ["PHASE", "HookPhase", "PHASES", "Ctx", "StepFn", "HookPredicate"]
