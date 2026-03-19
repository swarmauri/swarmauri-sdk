"""Hook-related decorators for Tigrbl v3."""

from __future__ import annotations

from enum import Enum
from typing import Iterable, Union

from tigrbl_core.config.constants import HOOK_DECLS_ATTR
from tigrbl_concrete._concrete import Hook
from tigrbl_runtime.runtime.exceptions import InvalidHookPhaseError
from tigrbl_atoms import HookPhase, HookPhases


def hook_ctx(ops: Union[str, Iterable[str]], *, phase: str | HookPhase | Enum):
    """Declare a ctx-only hook for one/many ops at a given phase."""

    phase_value = phase.value if isinstance(phase, Enum) else phase
    try:
        normalized_phase = HookPhase(phase_value)
    except ValueError as exc:
        raise InvalidHookPhaseError(
            phase=str(phase_value),
            allowed_phases=tuple(p.value for p in HookPhases),
        ) from exc

    def deco(fn):
        from .op import _ensure_cm, _unwrap

        cm = _ensure_cm(fn)
        f = _unwrap(cm)
        f.__tigrbl_ctx_only__ = True
        lst = getattr(f, HOOK_DECLS_ATTR, [])
        lst.append(Hook(phase=normalized_phase, fn=f, ops=ops))
        setattr(f, HOOK_DECLS_ATTR, lst)
        return cm

    return deco


__all__ = ["hook_ctx", "HOOK_DECLS_ATTR"]
