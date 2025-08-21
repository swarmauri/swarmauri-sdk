from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, Mapping, Optional


class ITokenService(ABC):
    """Stable interface to mint and verify tokens.

    Supports operations such as JSON Web Tokens (JWT) and JSON Web Signatures (JWS).
    The interface keeps crypto-agnostic policy fields explicit (``iss``, ``aud``,
    ``exp``, ``scope``).
    """

    @abstractmethod
    def supports(self) -> Mapping[str, Iterable[str]]:
        """Return formats and algorithms supported by the service."""

    @abstractmethod
    async def mint(
        self,
        claims: Dict[str, Any],
        *,
        alg: str,
        kid: str | None = None,
        key_version: int | None = None,
        headers: Optional[Dict[str, Any]] = None,
        lifetime_s: Optional[int] = 3600,
        issuer: Optional[str] = None,
        subject: Optional[str] = None,
        audience: Optional[str | list[str]] = None,
        scope: Optional[str] = None,
    ) -> str:
        """Return a compact JWS/JWT string with normalized timestamps."""

    @abstractmethod
    async def verify(
        self,
        token: str,
        *,
        issuer: Optional[str] = None,
        audience: Optional[str | list[str]] = None,
        leeway_s: int = 60,
    ) -> Dict[str, Any]:
        """Return validated claims or raise an exception on failure."""

    @abstractmethod
    async def jwks(self) -> dict:
        """Return a JWKS mapping (``{"keys": [...]}``) for signing key discovery."""
