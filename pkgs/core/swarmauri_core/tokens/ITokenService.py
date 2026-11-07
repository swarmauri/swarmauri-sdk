from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping


class ITokenService(ABC):
    """Stable interface to mint and verify tokens.

    Supports operations such as JSON Web Tokens (JWT) and JSON Web Signatures
    (JWS).
    The interface keeps crypto-agnostic policy fields explicit (``iss``,
    ``aud``,
    ``exp``, ``scope``).
    """

    @abstractmethod
    def supports(self) -> Mapping[str, Iterable[str]]:
        """Return formats and algorithms supported by the service."""

    @abstractmethod
    async def mint(
        self,
        claims: dict[str, Any],
        *,
        alg: str,
        kid: str | None = None,
        key_version: int | None = None,
        headers: dict[str, Any] | None = None,
        lifetime_s: int | None = 3600,
        issuer: str | None = None,
        subject: str | None = None,
        audience: str | list[str] | None = None,
        scope: str | None = None,
    ) -> str:
        """Return a compact JWS/JWT string with normalized timestamps."""

    @abstractmethod
    async def verify(
        self,
        token: str,
        *,
        issuer: str | None = None,
        audience: str | list[str] | None = None,
        leeway_s: int = 60,
    ) -> dict[str, Any]:
        """Return validated claims or raise an exception on failure."""

    @abstractmethod
    async def jwks(self) -> dict:
        """Return a JWKS mapping (``{"keys": [...]}``) for signing key
        discovery."""
