"""Base storage-layer primitives."""

from dataclasses import dataclass

from tigrbl_core._spec.storage_spec import ForeignKeySpec, StorageTransformSpec


@dataclass(frozen=True)
class ForeignKeyBase(ForeignKeySpec):
    """Base foreign-key configuration shared by concrete implementations."""


@dataclass(frozen=True)
class StorageTransformBase(StorageTransformSpec):
    """Base storage transform configuration shared by concrete implementations."""


__all__ = ["ForeignKeyBase", "StorageTransformBase"]
