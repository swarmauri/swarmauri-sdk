"""Backwards-compatible storage spec import path."""

from ..specs.storage_spec import (
    ForeignKey,
    ForeignKeySpec,
    StorageSpec,
    StorageTransform,
)

__all__ = ["StorageTransform", "ForeignKeySpec", "ForeignKey", "StorageSpec"]
