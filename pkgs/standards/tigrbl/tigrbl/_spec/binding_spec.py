from __future__ import annotations

from dataclasses import dataclass, field
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

    name: str
    spec: BindingSpec


@dataclass(slots=True)
class BindingRegistry:
    """Minimal in-memory registry for binding declarations."""

    _bindings: dict[str, BindingSpec] = field(default_factory=dict)

    def register(self, binding: Binding) -> None:
        self._bindings[binding.name] = binding.spec

    def get(self, name: str) -> BindingSpec | None:
        return self._bindings.get(name)

    def items(self) -> tuple[Binding, ...]:
        return tuple(
            Binding(name=name, spec=spec) for name, spec in self._bindings.items()
        )


def nested_prefix(model: Type) -> Optional[str]:
    """Return the user-supplied hierarchical prefix or ``None``."""

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
    "nested_prefix",
]
