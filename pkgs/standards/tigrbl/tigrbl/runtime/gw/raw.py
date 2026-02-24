from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Literal


@dataclass(slots=True)
class GwRawEnvelope:
    kind: Literal["asgi3"]
    scope: dict[str, Any]
    receive: Callable[[], Awaitable[dict[str, Any]]]
    send: Callable[[dict[str, Any]], Awaitable[None]]
