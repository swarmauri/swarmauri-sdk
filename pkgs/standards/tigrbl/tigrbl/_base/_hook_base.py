"""Base runtime hook wrapper for Tigrbl v3."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Union

from ..runtime.hook_types import HookPhase, StepFn
from .._spec.hook_spec import HookSpec


@dataclass(frozen=True, slots=True)
class HookBase(HookSpec):
    """Base hook bound to a phase and one or more ops."""

    phase: HookPhase
    fn: StepFn
    ops: Union[str, Iterable[str]] = "*"
    order: int = 0
    when: Optional[object] = None
    name: Optional[str] = None
    description: Optional[str] = None


__all__ = ["HookBase"]
