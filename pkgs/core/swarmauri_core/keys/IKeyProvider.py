from __future__ import annotations

from abc import ABC, abstractmethod

from .types import KeyRef


class IKeyProvider(ABC):
    """Interface for retrieving key material and JWKS documents."""

    @abstractmethod
    async def get_key(
        self, kid: str, version: int | None = None, *, include_secret: bool = False
    ) -> KeyRef:
        """Return a ``KeyRef`` for ``kid`` and ``version``."""

    @abstractmethod
    async def jwks(self) -> dict:
        """Return a JWKS mapping describing available public keys."""
