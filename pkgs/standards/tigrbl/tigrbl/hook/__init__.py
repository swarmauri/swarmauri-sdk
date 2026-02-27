"""Hook public API."""

from __future__ import annotations


def hook_ctx(*args, **kwargs):
    from ..decorators.hook import hook_ctx as _hook_ctx

    return _hook_ctx(*args, **kwargs)


__all__ = ["hook_ctx"]
