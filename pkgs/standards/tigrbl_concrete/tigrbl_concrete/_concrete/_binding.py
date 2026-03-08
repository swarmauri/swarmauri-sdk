from __future__ import annotations

from tigrbl_base._base import BindingBase, BindingRegistryBase


class Binding(BindingBase):
    """Concrete named binding declaration."""


class BindingRegistry(BindingRegistryBase):
    """Concrete named binding registry."""


__all__ = ["Binding", "BindingRegistry"]
