from __future__ import annotations

from tigrbl_core._spec.binding_spec import BindingRegistrySpec, BindingSpec


class BindingBase(BindingSpec):
    """Base named binding declaration."""


class BindingRegistryBase(BindingRegistrySpec):
    """Base named binding registry."""


__all__ = ["BindingBase", "BindingRegistryBase"]
