from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Tuple

Bytes = bytes
Headers = Dict[str, str]


class IHttpClient(ABC):
    """Interface for transports capable of issuing HTTP-style client requests."""

    @abstractmethod
    async def request(
        self,
        method: str,
        path: str,
        headers: Headers | None = None,
        body: Bytes = b"",
        **kwargs,
    ) -> Tuple[int, Headers, Bytes]: ...
