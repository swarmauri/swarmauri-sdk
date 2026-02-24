from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Union


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


__all__ = [
    "BindingSpec",
    "HttpJsonRpcBindingSpec",
    "HttpRestBindingSpec",
    "WsBindingSpec",
]
