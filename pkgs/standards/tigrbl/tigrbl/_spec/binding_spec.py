from __future__ import annotations

from dataclasses import dataclass, field
from dataclasses import dataclass
from typing import Literal, Optional, Type, Union

from ..config.constants import TIGRBL_NESTED_PATHS_ATTR


@dataclass(frozen=True, slots=True)
class HttpRestBindingSpec:
    proto: Literal["http.rest", "https.rest"]
    methods: tuple[str, ...]
    path: str


@dataclass(frozen=True, slots=True)
class HttpJsonRpcBindingSpec:
    proto: Literal["http.jsonrpc", "https.jsonrpc"]
    rpc_method: str


@dataclass(frozen=True, slots=True)
class WsBindingSpec:
    proto: Literal["ws", "wss"]
    path: str
    subprotocols: tuple[str, ...] = ()


BindingSpec = Union[HttpRestBindingSpec, HttpJsonRpcBindingSpec, WsBindingSpec]


@dataclass(frozen=True, slots=True)
class Binding:
    """Named binding declaration used for registry composition."""
    """Named binding wrapper used by registries and planners."""

    name: str
    spec: BindingSpec


@dataclass(slots=True)
class BindingRegistry:
    """Simple in-memory registry for named transport bindings."""

    _bindings: dict[str, Binding]

    def __init__(self) -> None:
        self._bindings = {}

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


__all__ = [
    "Binding",
    "BindingRegistry",
    "BindingSpec",
    "HttpJsonRpcBindingSpec",
    "HttpRestBindingSpec",
    "WsBindingSpec",
    "resolve_rest_nested_prefix",
]
