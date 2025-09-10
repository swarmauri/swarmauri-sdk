"""Hook specification for Tigrbl v3."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .types import HookPhase, StepFn, HookPredicate


@dataclass(frozen=True, slots=True)
class HookSpec:
    phase: HookPhase
    fn: StepFn
    order: int = 0
    when: Optional[HookPredicate] = None
    name: Optional[str] = None
    description: Optional[str] = None


# Backwards compatibility alias
OpHook = HookSpec

__all__ = ["HookSpec", "OpHook"]
