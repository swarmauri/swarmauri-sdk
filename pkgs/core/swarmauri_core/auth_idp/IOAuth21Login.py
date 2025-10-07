from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping


class IOAuth21Login(ABC):
    """Contract for OAuth 2.1 user login flows."""

    @abstractmethod
    async def auth_url(self) -> Mapping[str, str]:
        """Return the authorization URL payload for initiating login."""
        ...

    @abstractmethod
    async def exchange_and_identity(self, code: str, state: str) -> Mapping[str, Any]:
        """Exchange the authorization code and return normalized identity claims."""
        ...
