"""Runtime hook wrapper for Tigrbl v3."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Union

from ..hook.types import HookPhase, StepFn
from ..specs.hook_spec import HookSpec


@dataclass(frozen=True, slots=True)
class Hook(HookSpec):
    """Concrete hook bound to a phase and one or more ops."""

    phase: HookPhase
    fn: StepFn
    ops: Union[str, Iterable[str]] = "*"
    order: int = 0
    when: Optional[object] = None
    name: Optional[str] = None
    description: Optional[str] = None


__all__ = ["Hook"]
