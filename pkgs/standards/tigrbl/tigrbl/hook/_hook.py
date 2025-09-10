"""Runtime hook wrapper for Tigrbl v3."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Union

from .types import HookPhase, StepFn


@dataclass(frozen=True, slots=True)
class Hook:
    """Concrete hook bound to a phase and one or more ops."""

    phase: HookPhase
    fn: StepFn
    ops: Union[str, Iterable[str]]
    name: Optional[str] = None
    description: Optional[str] = None


__all__ = ["Hook"]
