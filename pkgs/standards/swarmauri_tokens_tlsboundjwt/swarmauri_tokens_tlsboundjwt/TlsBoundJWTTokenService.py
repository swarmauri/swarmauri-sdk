from __future__ import annotations

import base64
import hashlib
from typing import Callable, Dict, Iterable, Mapping, Optional, Literal

from swarmauri_providers.tokens import JWTTokenService
from swarmauri_core.crypto.types import JWAAlg
from swarmauri_core.key_providers import IKeyProvider


def _b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")


def x5tS256_from_der(cert_der: bytes) -> str:
    """RFC 8705: SHA-256 over DER, base64url without padding."""
    return _b64u(hashlib.sha256(cert_der).digest())


class TlsBoundJWTTokenService(JWTTokenService):
    """
    mTLS-bound JWTs per RFC 8705 using the 'cnf' claim:
      cnf: { "x5t#S256": "<base64url sha-256 of client cert DER>" }

    Verification requires access to the *current request's* client certificate.
    Provide a getter that returns the DER bytes, or pre-computed x5t#S256.
    """

    type: Literal["TlsBoundJWTTokenService"] = "TlsBoundJWTTokenService"

    def __init__(
        self,
        key_provider: IKeyProvider,
        *,
        default_issuer: Optional[str] = None,
        client_cert_der_getter: Optional[Callable[[], Optional[bytes]]] = None,
        client_cert_x5tS256_getter: Optional[Callable[[], Optional[str]]] = None,
    ) -> None:
        super().__init__(key_provider, default_issuer=default_issuer)
        self._get_der = client_cert_der_getter
        self._get_x5t = client_cert_x5tS256_getter

    def supports(self) -> Mapping[str, Iterable[JWAAlg]]:
        base = super().supports()
        return {"formats": (*base["formats"], "JWT"), "algs": base["algs"]}

    # Helper to compute or fetch the live fingerprint
    def _live_x5tS256(self) -> Optional[str]:
        if self._get_x5t:
            v = self._get_x5t()
            if v:
                return v
        if self._get_der:
            der = self._get_der()
            if der:
                return x5tS256_from_der(der)
        return None

    async def mint(
        self,
        claims: Dict[str, object],
        *,
        alg: JWAAlg,
        kid: str | None = None,
        key_version: int | None = None,
        headers: Optional[Dict[str, object]] = None,
        lifetime_s: Optional[int] = 3600,
        issuer: Optional[str] = None,
        subject: Optional[str] = None,
        audience: Optional[str | list[str]] = None,
        scope: Optional[str] = None,
    ) -> str:
        # Respect explicit cnf if caller already set it.
        if "cnf" not in claims:
            x5t = self._live_x5tS256()
            if x5t:
                claims = dict(claims)
                claims["cnf"] = {"x5t#S256": x5t}
        return await super().mint(
            claims,
            alg=alg,
            kid=kid,
            key_version=key_version,
            headers=headers,
            lifetime_s=lifetime_s,
            issuer=issuer,
            subject=subject,
            audience=audience,
            scope=scope,
        )

    async def verify(
        self,
        token: str,
        *,
        issuer: Optional[str] = None,
        audience: Optional[str | list[str]] = None,
        leeway_s: int = 60,
    ) -> Dict[str, object]:
        claims = await super().verify(
            token, issuer=issuer, audience=audience, leeway_s=leeway_s
        )
        cnf = claims.get("cnf") if isinstance(claims, dict) else None
        bound = cnf.get("x5t#S256") if isinstance(cnf, dict) else None
        if not bound:
            raise ValueError("mTLS-bound token missing cnf.x5t#S256")

        live = self._live_x5tS256()
        if not live:
            raise ValueError("mTLS verification requires the live client certificate")
        if live != bound:
            raise ValueError("mTLS binding mismatch (x5t#S256)")
        return claims
