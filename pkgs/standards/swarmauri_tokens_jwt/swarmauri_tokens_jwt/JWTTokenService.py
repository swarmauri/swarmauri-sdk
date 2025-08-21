from __future__ import annotations

import time
from typing import Any, Dict, Iterable, Literal, Mapping, Optional

import jwt
from jwt import algorithms

from swarmauri_base.tokens import TokenServiceBase
from swarmauri_core.keys import IKeyProvider, KeyAlg

ALG_MAP_SIGN = {
    "RS256": KeyAlg.RSA_PSS_SHA256,
    "PS256": KeyAlg.RSA_PSS_SHA256,
    "ES256": KeyAlg.ECDSA_P256_SHA256,
    "EdDSA": KeyAlg.ED25519,
    "HS256": KeyAlg.HMAC_SHA256,
}


class JWTTokenService(TokenServiceBase):
    """JWS/JWT issuer and verifier backed by an ``IKeyProvider``."""

    type: Literal["JWTTokenService"] = "JWTTokenService"

    def __init__(
        self, key_provider: IKeyProvider, *, default_issuer: Optional[str] = None
    ) -> None:
        super().__init__()
        self._kp = key_provider
        self._iss = default_issuer

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {"formats": ("JWT", "JWS"), "algs": tuple(ALG_MAP_SIGN.keys())}

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
        now = int(time.time())
        payload = dict(claims)
        payload.setdefault("iat", now)
        payload.setdefault("nbf", now)
        if lifetime_s:
            payload.setdefault("exp", now + int(lifetime_s))
        if issuer or self._iss:
            payload.setdefault("iss", issuer or self._iss)
        if subject:
            payload.setdefault("sub", subject)
        if audience:
            payload.setdefault("aud", audience)
        if scope:
            payload.setdefault("scope", scope)

        headers = dict(headers or {})

        if alg == "HS256":
            if not kid:
                raise ValueError("HS256 mint requires 'kid' of a symmetric key")
            ref = await self._kp.get_key(kid, key_version, include_secret=True)
            if ref.material is None:
                raise RuntimeError("HMAC secret is not exportable under current policy")
            key = ref.material
            headers.setdefault("kid", f"{ref.kid}.{ref.version}")
            return jwt.encode(payload, key, algorithm="HS256", headers=headers)

        if not kid:
            raise ValueError("asymmetric mint requires 'kid' of a signing key")
        ref = await self._kp.get_key(kid, key_version, include_secret=True)
        headers.setdefault("kid", f"{ref.kid}.{ref.version}")

        key = ref.material
        if key is None:
            raise RuntimeError("Signing key is not exportable under current policy")

        return jwt.encode(payload, key, algorithm=alg, headers=headers)

    async def verify(
        self,
        token: str,
        *,
        issuer: Optional[str] = None,
        audience: Optional[str | list[str]] = None,
        leeway_s: int = 60,
    ) -> Dict[str, Any]:
        jwks = await self._kp.jwks()

        def _key_resolver(hdr: dict[str, Any], payload: dict[str, Any]) -> Any:
            kid = hdr.get("kid")
            if not kid:
                return None
            for jwk in jwks.get("keys", []):
                if jwk.get("kid") != kid:
                    continue
                kty = jwk.get("kty")
                if kty == "RSA":
                    return algorithms.RSAAlgorithm.from_jwk(jwk)
                if kty == "EC":
                    return algorithms.ECAlgorithm.from_jwk(jwk)
                if kty == "OKP" and jwk.get("crv") == "Ed25519":
                    return algorithms.Ed25519Algorithm.from_jwk(jwk)
                if kty == "oct":
                    return algorithms.HMACAlgorithm.from_jwk(jwk)
            return None

        hdr = jwt.get_unverified_header(token)
        key = _key_resolver(hdr, {})

        options = {"verify_aud": audience is not None}
        return jwt.decode(
            token,
            key=key,
            algorithms=list(self.supports()["algs"]),
            audience=audience,
            issuer=issuer or self._iss,
            leeway=leeway_s,
            options=options,
        )

    async def jwks(self) -> dict:
        return await self._kp.jwks()
