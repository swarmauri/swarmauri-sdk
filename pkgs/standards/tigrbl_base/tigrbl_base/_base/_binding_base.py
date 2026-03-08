from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Type

from tigrbl_core.config.constants import TIGRBL_NESTED_PATHS_ATTR
from tigrbl_core._spec.binding_spec import Binding, BindingRegistry, BindingSpec
from tigrbl_core._spec.serde import SerdeMixin


@dataclass(frozen=True, slots=True)
class BindingBase(SerdeMixin, Binding):
    """Base binding implementation shared by concrete wrappers."""

    name: str
    spec: BindingSpec


@dataclass(slots=True)
class BindingRegistryBase(BindingRegistry):
    """Base in-memory registry for named transport bindings."""

    _bindings: dict[str, Binding] = field(default_factory=dict)

    def register(self, binding: Binding) -> None:
        self._bindings[binding.name] = binding

    def get(self, name: str) -> Optional[Binding]:
        return self._bindings.get(name)

    def values(self) -> tuple[Binding, ...]:
        return tuple(self._bindings.values())


def resolve_rest_nested_prefix(model: Type) -> Optional[str]:
    """Return the configured nested REST prefix for ``model`` if present."""

    cb = getattr(model, TIGRBL_NESTED_PATHS_ATTR, None)
    if callable(cb):
        return cb()
    return getattr(model, "_nested_path", None)


__all__ = ["BindingBase", "BindingRegistryBase", "resolve_rest_nested_prefix"]
