"""Concrete storage-layer primitives."""

from dataclasses import dataclass

from .._base._storage import ForeignKeyBase


@dataclass(frozen=True)
class ForeignKey(ForeignKeyBase):
    """Concrete foreign key configuration used at runtime."""


__all__ = ["ForeignKey"]
