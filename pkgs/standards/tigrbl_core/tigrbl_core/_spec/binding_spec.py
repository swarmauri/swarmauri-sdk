from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional, Type, Union

from ..config.constants import TIGRBL_NESTED_PATHS_ATTR
from .serde import SerdeMixin


@dataclass(frozen=True, slots=True)
class HttpRestBindingSpec(SerdeMixin):
    proto: Literal["http.rest", "https.rest"]
    methods: tuple[str, ...]
    path: str


@dataclass(frozen=True, slots=True)
class HttpJsonRpcBindingSpec(SerdeMixin):
    proto: Literal["http.jsonrpc", "https.jsonrpc"]
    rpc_method: str


@dataclass(frozen=True, slots=True)
class WsBindingSpec(SerdeMixin):
    proto: Literal["ws", "wss"]
    path: str
    subprotocols: tuple[str, ...] = ()


BindingTargetSpec = Union[HttpRestBindingSpec, HttpJsonRpcBindingSpec, WsBindingSpec]


@dataclass(frozen=True, slots=True)
class BindingSpec(SerdeMixin):
    """Concrete named binding declaration."""

    name: str
    spec: BindingTargetSpec


@dataclass(slots=True)
class BindingRegistrySpec(SerdeMixin):
    """Concrete named binding registry."""

    _bindings: dict[str, BindingSpec]

    def __init__(self) -> None:
        self._bindings = {}

    def register(self, binding: BindingSpec) -> None:
        self._bindings[binding.name] = binding

    def get(self, name: str) -> Optional[BindingSpec]:
        return self._bindings.get(name)

    def values(self) -> tuple[BindingSpec, ...]:
        return tuple(self._bindings.values())


def resolve_rest_nested_prefix(model: Type) -> Optional[str]:
    """Return the configured nested REST prefix for ``model`` if present."""

    cb = getattr(model, TIGRBL_NESTED_PATHS_ATTR, None)
    if callable(cb):
        return cb()
    return getattr(model, "_nested_path", None)


__all__ = [
    "BindingSpec",
    "BindingRegistrySpec",
    "BindingTargetSpec",
    "HttpJsonRpcBindingSpec",
    "HttpRestBindingSpec",
    "WsBindingSpec",
    "resolve_rest_nested_prefix",
]
