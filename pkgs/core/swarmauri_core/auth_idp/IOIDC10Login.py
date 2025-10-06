from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping


class IOIDC10Login(ABC):
    """Contract for OpenID Connect 1.0 user login flows."""

    @abstractmethod
    async def auth_url(self) -> Mapping[str, str]:
        """Return the authorization URL payload for initiating login."""
        ...

    @abstractmethod
    async def exchange(self, code: str, state: str) -> Mapping[str, Any]:
        """Exchange the authorization code and return normalized identity claims."""
        ...
