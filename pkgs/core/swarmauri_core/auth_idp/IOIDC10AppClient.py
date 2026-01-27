from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class IOIDC10AppClient(ABC):
    """Contract for OIDC 1.0 machine-to-machine token flows."""

    @abstractmethod
    async def access_token(self, scope: Optional[str] = None) -> str:
        """Return a bearer token constrained to the optional scope."""
        ...
