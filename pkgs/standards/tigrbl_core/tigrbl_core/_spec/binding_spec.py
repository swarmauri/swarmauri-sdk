from __future__ import annotations

from dataclasses import dataclass, field
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


TransportBindingSpec = Union[
    HttpRestBindingSpec,
    HttpJsonRpcBindingSpec,
    WsBindingSpec,
]


@dataclass(frozen=True, slots=True)
class BindingSpec(SerdeMixin):
    """Named binding declaration used for registry composition."""

    name: str
    spec: TransportBindingSpec


@dataclass(slots=True)
class BindingRegistrySpec(SerdeMixin):
    """Simple in-memory registry for named transport bindings."""

    _bindings: dict[str, BindingSpec] = field(default_factory=dict)

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
    "HttpJsonRpcBindingSpec",
    "HttpRestBindingSpec",
    "TransportBindingSpec",
    "WsBindingSpec",
    "resolve_rest_nested_prefix",
]
