"""Base storage-layer primitives."""

from dataclasses import dataclass

from .._spec.storage_spec import ForeignKeySpec


@dataclass(frozen=True)
class ForeignKeyBase(ForeignKeySpec):
    """Base foreign-key configuration shared by concrete implementations."""


__all__ = ["ForeignKeyBase"]
