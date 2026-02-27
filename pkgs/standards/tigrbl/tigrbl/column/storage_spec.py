"""Backward-compatible imports for storage spec definitions."""

from .._concrete._storage import ForeignKey
from .._spec.storage_spec import ForeignKeySpec, StorageSpec, StorageTransform

__all__ = ["ForeignKey", "ForeignKeySpec", "StorageSpec", "StorageTransform"]
