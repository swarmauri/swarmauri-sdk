from __future__ import annotations

import json
import time
from typing import Any, Dict, Iterable, Literal, Mapping, Optional

from cryptography.hazmat.primitives import serialization

from swarmauri_base.tokens import TokenServiceBase
from swarmauri_core.crypto.types import JWAAlg
from swarmauri_core.keys import IKeyProvider
from swarmauri_signing_jws import JwsSignerVerifier

# Supported algorithms for signing/verifying.
ALG_MAP_SIGN: Mapping[JWAAlg, str] = {
    JWAAlg.RS256: "RSA",
    JWAAlg.PS256: "RSA",
    JWAAlg.ES256: "EC",
    JWAAlg.EDDSA: "OKP",
    JWAAlg.HS256: "oct",
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
        self._jws = JwsSignerVerifier()

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

        if not kid:
            raise ValueError("mint requires 'kid' of a signing key")

        ref = await self._kp.get_key(kid, key_version, include_secret=True)
        kid_header = headers.pop("kid", f"{ref.kid}.{ref.version}")

        if alg == JWAAlg.HS256:
            if ref.material is None:
                raise RuntimeError("HMAC secret is not exportable under current policy")
            key_obj: Mapping[str, Any] = {"kind": "raw", "key": ref.material}
        else:
            if ref.material is None:
                raise RuntimeError("Signing key is not exportable under current policy")
            priv = serialization.load_pem_private_key(ref.material, password=None)
            key_obj = {"kind": "cryptography_obj", "obj": priv}

        token = await self._jws.sign_compact(
            payload=payload,
            alg=alg,
            key=key_obj,
            kid=kid_header,
            header_extra=headers or None,
        )
        return token

    async def verify(
        self,
        token: str,
        *,
        issuer: Optional[str] = None,
        audience: Optional[str | list[str]] = None,
        leeway_s: int = 60,
    ) -> Dict[str, Any]:
        jwks = await self._kp.jwks()

        def _resolver(kid: str | None, alg: str) -> Optional[Mapping[str, Any]]:
            if not kid:
                return None
            for jwk in jwks.get("keys", []):
                if jwk.get("kid") == kid:
                    return jwk
            return None

        res = await self._jws.verify_compact(
            token,
            jwks_resolver=_resolver,
            alg_allowlist=self.supports()["algs"],
        )

        payload: Dict[str, Any] = json.loads(res.payload)

        now = int(time.time())
        exp = payload.get("exp")
        if exp is not None and now > int(exp) + leeway_s:
            raise ValueError("token expired")
        nbf = payload.get("nbf")
        if nbf is not None and now + leeway_s < int(nbf):
            raise ValueError("token not yet valid")

        iss_expected = issuer or self._iss
        if iss_expected and payload.get("iss") != iss_expected:
            raise ValueError("issuer mismatch")

        if audience is not None:
            aud_claim = payload.get("aud")
            if isinstance(aud_claim, str):
                aud_list = [aud_claim]
            elif isinstance(aud_claim, list):
                aud_list = aud_claim
            else:
                raise ValueError("audience claim missing")
            exp_aud = audience if isinstance(audience, list) else [audience]
            if not any(a in aud_list for a in exp_aud):
                raise ValueError("audience mismatch")

        return payload

    async def jwks(self) -> dict:
        return await self._kp.jwks()
