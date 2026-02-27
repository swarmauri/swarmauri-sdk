"""Concrete runtime hook wrapper for Tigrbl v3."""

from __future__ import annotations

from .._base._hook import HookBase


class Hook(HookBase):
    """Concrete hook implementation."""


__all__ = ["Hook"]
