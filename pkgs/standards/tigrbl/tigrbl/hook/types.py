"""Hook type definitions exposed without importing runtime package internals."""

from __future__ import annotations

from tigrbl_atoms import HookPhase, HookPhases, HookPredicate, StepFn

PHASE = HookPhase
PHASES = tuple(h.value for h in HookPhases)

__all__ = ["HookPhase", "HookPhases", "PHASE", "PHASES", "StepFn", "HookPredicate"]
