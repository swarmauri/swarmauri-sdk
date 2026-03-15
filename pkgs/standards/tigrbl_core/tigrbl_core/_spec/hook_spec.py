"""Hook specification for Tigrbl v3."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from tigrbl_atoms import HookPhase, HookPredicate, StepFn

from .serde import SerdeMixin


@dataclass(frozen=True, slots=True)
class HookSpec(SerdeMixin):
    phase: HookPhase
    fn: StepFn
    order: int = 0
    when: Optional[HookPredicate] = None
    name: Optional[str] = None
    description: Optional[str] = None

    @classmethod
    def collect(cls, owner: type) -> tuple["HookSpec", ...]:
        hooks: list[HookSpec] = []
        for hook in getattr(owner, "HOOKS", ()) or ():
            if isinstance(hook, HookSpec):
                hooks.append(hook)
            elif isinstance(hook, dict):
                hooks.append(cls(**hook))
        for _, attr in vars(owner).items():
            declared = getattr(attr, "__tigrbl_hook_spec__", None)
            if isinstance(declared, HookSpec):
                hooks.append(declared)
            elif isinstance(declared, dict):
                hooks.append(cls(**declared))
        return tuple(hooks)


# Backwards compatibility alias
OpHook = HookSpec

__all__ = ["HookSpec", "OpHook"]
