"""Concrete storage-layer primitives."""

from dataclasses import dataclass

from tigrbl_base._base._storage import ForeignKeyBase, StorageTransformBase


@dataclass(frozen=True)
class ForeignKey(ForeignKeyBase):
    """Concrete foreign key configuration used at runtime."""


@dataclass(frozen=True)
class StorageTransform(StorageTransformBase):
    """Concrete storage transform configuration used at runtime."""


__all__ = ["ForeignKey", "StorageTransform"]
