"""Backward-compatible imports for storage spec definitions."""

from ..specs.storage_spec import (
    ForeignKey,
    ForeignKeySpec,
    StorageSpec,
    StorageTransform,
)

__all__ = ["ForeignKey", "ForeignKeySpec", "StorageSpec", "StorageTransform"]
