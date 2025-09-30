from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Awaitable, Dict, Tuple

Bytes = bytes
Headers = Dict[str, str]


class HttpApp(ABC):
    """Minimal HTTP-like application contract."""

    @abstractmethod
    def __call__(
        self,
        method: str,
        path: str,
        headers: Headers,
        body: Bytes,
    ) -> Awaitable[Tuple[int, Headers, Bytes]]: ...


class IAppServer(ABC):
    """Interface for transports that terminate an HTTP-style application."""

    @abstractmethod
    def set_app(self, app: HttpApp) -> None: ...
