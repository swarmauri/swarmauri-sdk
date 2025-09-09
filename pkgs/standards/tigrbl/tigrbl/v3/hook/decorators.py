"""Hook-related decorators for Tigrbl v3."""

from __future__ import annotations

from typing import Iterable, Union

from ..config.constants import HOOK_DECLS_ATTR
from ._hook import Hook


def hook_ctx(ops: Union[str, Iterable[str]], *, phase: str):
    """Declare a ctx-only hook for one/many ops at a given phase."""

    def deco(fn):
        from ..op.decorators import _ensure_cm, _unwrap

        cm = _ensure_cm(fn)
        f = _unwrap(cm)
        f.__tigrbl_ctx_only__ = True
        lst = getattr(f, HOOK_DECLS_ATTR, [])
        lst.append(Hook(phase=phase, fn=f, ops=ops))
        setattr(f, HOOK_DECLS_ATTR, lst)
        return cm

    return deco


__all__ = ["hook_ctx", "HOOK_DECLS_ATTR"]
