"""Base operation descriptor implementation for Tigrbl."""

from __future__ import annotations

from tigrbl_core.tigrbl._spec.op_spec import OpSpec


class OpBase(OpSpec):
    """Base operation descriptor type."""


__all__ = ["OpBase"]
