"""Concrete runtime hook wrapper for Tigrbl v3."""

from __future__ import annotations

from tigrbl_base.tigrbl._base._hook_base import HookBase


class Hook(HookBase):
    """Concrete hook implementation."""


__all__ = ["Hook"]
