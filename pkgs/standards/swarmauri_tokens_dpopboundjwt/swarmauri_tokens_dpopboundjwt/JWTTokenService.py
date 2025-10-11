from __future__ import annotations

import time
from typing import Iterable, Mapping, Optional

import jwt

from swarmauri_core.crypto.types import JWAAlg
from swarmauri_core.key_providers.IKeyProvider import IKeyProvider


class JWTTokenService:
    """Basic JWT minting and verification service."""

    type = "JWTTokenService"

    def __init__(
        self, key_provider: IKeyProvider, *, default_issuer: Optional[str] = None
    ) -> None:
        self._keys = key_provider
        self._issuer = default_issuer

    def supports(self) -> Mapping[str, Iterable[JWAAlg]]:
        return {
            "formats": ("JWT",),
            "algs": (
                JWAAlg.HS256,
                JWAAlg.RS256,
                JWAAlg.PS256,
                JWAAlg.ES256,
                JWAAlg.EDDSA,
            ),
        }

    async def mint(
        self,
        claims: dict[str, object],
        *,
        alg: JWAAlg,
        kid: str | None = None,
        key_version: int | None = None,
        headers: Optional[dict[str, object]] = None,
        lifetime_s: Optional[int] = 3600,
        issuer: Optional[str] = None,
        subject: Optional[str] = None,
        audience: Optional[str | list[str]] = None,
        scope: Optional[str] = None,
    ) -> str:
        now = int(time.time())
        payload = dict(claims)
        if issuer or self._issuer:
            payload["iss"] = issuer or self._issuer
        if subject:
            payload["sub"] = subject
        if audience:
            payload["aud"] = audience
        if scope:
            payload["scope"] = scope
        if lifetime_s is not None:
            payload["iat"] = now
            payload["exp"] = now + int(lifetime_s)

        kid = kid or "default"
        keyref = await self._keys.get_key(kid, version=key_version, include_secret=True)
        secret = keyref.material or b""
        return jwt.encode(
            payload,
            secret,
            algorithm=alg.value,
            headers={"kid": kid, **(headers or {})},
        )

    async def verify(
        self,
        token: str,
        *,
        issuer: Optional[str] = None,
        audience: Optional[str | list[str]] = None,
        leeway_s: int = 60,
    ) -> dict[str, object]:
        hdr = jwt.get_unverified_header(token)
        alg = JWAAlg(hdr.get("alg"))
        kid = hdr.get("kid", "default")
        keyref = await self._keys.get_key(kid, include_secret=True)
        secret = keyref.material or b""
        return jwt.decode(
            token,
            key=secret,
            algorithms=[alg.value],
            issuer=issuer or self._issuer,
            audience=audience,
            leeway=leeway_s,
        )
