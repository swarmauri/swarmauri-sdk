"""Shortcut helpers for building Hook specs."""

from __future__ import annotations

from typing import Iterable, Union

from .types import HookPhase, HookPredicate, StepFn
from ._hook import Hook
from .hook_spec import HookSpec


def hook(
    phase: HookPhase,
    ops: Union[str, Iterable[str]],
    fn: StepFn,
    *,
    name: str | None = None,
    description: str | None = None,
) -> Hook:
    """Build a :class:`Hook` instance."""
    return Hook(phase=phase, fn=fn, ops=ops, name=name, description=description)


def hook_spec(
    phase: HookPhase,
    fn: StepFn,
    *,
    order: int = 0,
    when: HookPredicate | None = None,
    name: str | None = None,
    description: str | None = None,
) -> HookSpec:
    """Build a :class:`HookSpec` instance."""
    return HookSpec(
        phase=phase,
        fn=fn,
        order=order,
        when=when,
        name=name,
        description=description,
    )


__all__ = ["hook", "hook_spec"]
