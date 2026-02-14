"""Hook-related decorators for Tigrbl v3."""

from __future__ import annotations

from enum import Enum
from typing import Iterable, Union

from ..config.constants import HOOK_DECLS_ATTR
from ._hook import Hook
from .exceptions import InvalidHookPhaseError
from .types import PHASE, PHASES


def hook_ctx(ops: Union[str, Iterable[str]], *, phase: str | PHASE | Enum):
    """Declare a ctx-only hook for one/many ops at a given phase."""

    normalized_phase = phase.value if isinstance(phase, Enum) else phase
    if normalized_phase not in PHASES:
        raise InvalidHookPhaseError(phase=str(normalized_phase), allowed_phases=PHASES)

    def deco(fn):
        from ..op.decorators import _ensure_cm, _unwrap

        cm = _ensure_cm(fn)
        f = _unwrap(cm)
        f.__tigrbl_ctx_only__ = True
        lst = getattr(f, HOOK_DECLS_ATTR, [])
        lst.append(Hook(phase=normalized_phase, fn=f, ops=ops))
        setattr(f, HOOK_DECLS_ATTR, lst)
        return cm

    return deco


__all__ = ["hook_ctx", "HOOK_DECLS_ATTR"]
