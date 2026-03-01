from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Literal, Mapping, Sequence


@dataclass(slots=True)
class GwRawEnvelope:
    kind: Literal["asgi3"]
    scope: dict[str, Any]
    receive: Callable[[], Awaitable[dict[str, Any]]]
    send: Callable[[dict[str, Any]], Awaitable[None]]


@dataclass(frozen=True, slots=True)
class GwRouteEnvelope:
    transport: Literal["http", "ws", "sse", "stream", "http3"]
    scheme: Literal["http", "https", "ws", "wss", "h3"]
    kind: Literal["rest", "jsonrpc", "maybe-jsonrpc", "unknown"]
    method: str | None
    path: str | None
    headers: Mapping[str, str]
    query: Mapping[str, Sequence[str]]
    body: bytes | None
    ws_event: Any | None
    rpc: Mapping[str, Any] | None
