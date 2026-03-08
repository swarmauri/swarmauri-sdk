from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal, Optional, Union

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


BindingSpec = Union[HttpRestBindingSpec, HttpJsonRpcBindingSpec, WsBindingSpec]


class Binding(ABC):
    """Core interface for named binding declarations."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def spec(self) -> BindingSpec: ...


class BindingRegistry(ABC):
    """Core interface for named binding registries."""

    @abstractmethod
    def register(self, binding: Binding) -> None: ...

    @abstractmethod
    def get(self, name: str) -> Optional[Binding]: ...

    @abstractmethod
    def values(self) -> tuple[Binding, ...]: ...


__all__ = [
    "Binding",
    "BindingRegistry",
    "BindingSpec",
    "HttpJsonRpcBindingSpec",
    "HttpRestBindingSpec",
    "WsBindingSpec",
]
