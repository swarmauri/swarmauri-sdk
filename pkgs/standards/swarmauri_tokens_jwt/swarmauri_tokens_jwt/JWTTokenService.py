from __future__ import annotations

import time
from typing import Any, Dict, Iterable, Literal, Mapping, Optional

import jwt
from jwt import algorithms

from swarmauri_base.tokens import TokenServiceBase
from swarmauri_core.crypto.types import JWAAlg
from swarmauri_core.keys import IKeyProvider, KeyAlg

ALG_MAP_SIGN = {
    JWAAlg.RS256: KeyAlg.RSA_PSS_SHA256,
    JWAAlg.PS256: KeyAlg.RSA_PSS_SHA256,
    JWAAlg.ES256: KeyAlg.ECDSA_P256_SHA256,
    JWAAlg.EDDSA: KeyAlg.ED25519,
    JWAAlg.HS256: KeyAlg.HMAC_SHA256,
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

    def supports(self) -> Mapping[str, Iterable[JWAAlg]]:
        return {"formats": ("JWT", "JWS"), "algs": tuple(ALG_MAP_SIGN.keys())}

    async def mint(
        self,
        claims: Dict[str, Any],
        *,
        alg: JWAAlg,
        kid: str | None = None,
        key_version: int | None = None,
        headers: Optional[Dict[str, Any]] = None,
        lifetime_s: Optional[int] = 3600,
        issuer: Optional[str] = None,
        subject: Optional[str] = None,
        audience: Optional[str | list[str]] = None,
        scope: Optional[str] = None,
        include_iat: bool = True,
        include_nbf: bool = True,
    ) -> str:
        now = int(time.time())
        payload = dict(claims)
        if include_iat:
            payload.setdefault("iat", now)
        if include_nbf:
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

        if alg == JWAAlg.HS256:
            if not kid:
                raise ValueError("HS256 mint requires 'kid' of a symmetric key")
            ref = await self._kp.get_key(kid, key_version, include_secret=True)
            if ref.material is None:
                raise RuntimeError("HMAC secret is not exportable under current policy")
            key = ref.material
            headers.setdefault("kid", f"{ref.kid}.{ref.version}")
            return jwt.encode(payload, key, algorithm=alg.value, headers=headers)

        if not kid:
            raise ValueError("asymmetric mint requires 'kid' of a signing key")
        ref = await self._kp.get_key(kid, key_version, include_secret=True)
        headers.setdefault("kid", f"{ref.kid}.{ref.version}")

        key = ref.material
        if key is None:
            raise RuntimeError("Signing key is not exportable under current policy")

        return jwt.encode(payload, key, algorithm=alg.value, headers=headers)

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
                if kty == "OKP":
                    return algorithms.OKPAlgorithm.from_jwk(jwk)
                if kty == "oct":
                    return algorithms.HMACAlgorithm.from_jwk(jwk)
            return None

        hdr = jwt.get_unverified_header(token)
        key = _key_resolver(hdr, {})

        options = {"verify_aud": audience is not None, "verify_iat": False}
        return jwt.decode(
            token,
            key=key,
            algorithms=[a.value for a in self.supports()["algs"]],
            audience=audience,
            issuer=issuer or self._iss,
            leeway=leeway_s,
            options=options,
        )

    async def jwks(self) -> dict:
        return await self._kp.jwks()
