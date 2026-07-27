from __future__ import annotations

from abc import ABC, abstractmethod


class IOAuth20AppClient(ABC):
    """Contract for OAuth 2.0 machine-to-machine token flows."""

    @abstractmethod
    async def access_token(self, scope: str | None = None) -> str:
        """Return a bearer token constrained to the optional scope."""
        ...
