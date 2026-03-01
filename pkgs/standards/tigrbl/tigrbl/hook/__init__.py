"""Hook public API."""

from __future__ import annotations

from .._spec.hook_spec import HookSpec, OpHook

def hook_ctx(*args, **kwargs):
    from ..decorators.hook import hook_ctx as _hook_ctx

    return _hook_ctx(*args, **kwargs)


__all__ = ["HookSpec", "OpHook", "hook_ctx"]
