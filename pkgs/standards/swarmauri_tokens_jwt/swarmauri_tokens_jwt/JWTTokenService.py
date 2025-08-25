from __future__ import annotations

import json
import time
from typing import Any, Dict, Iterable, Literal, Mapping, Optional

from swarmauri_base.tokens import TokenServiceBase
from swarmauri_core.crypto.types import JWAAlg, KeyRef
from swarmauri_core.keys import IKeyProvider, KeyAlg
from swarmauri_signing_jws import JwsSignerVerifier

ALG_MAP_SIGN = {
    JWAAlg.RS256: KeyAlg.RSA_PSS_SHA256,
    JWAAlg.PS256: KeyAlg.RSA_PSS_SHA256,
    JWAAlg.ES256: KeyAlg.ECDSA_P256_SHA256,
    JWAAlg.EDDSA: KeyAlg.ED25519,
    JWAAlg.HS256: KeyAlg.HMAC_SHA256,
}


def _ref_to_signing_key(ref: KeyRef, alg: JWAAlg) -> Mapping[str, Any]:
    """Convert a ``KeyRef`` into a ``JwsSignerVerifier`` key mapping."""
    mat = ref.material
    if mat is None:
        raise RuntimeError("key material not available for signing")
    if alg == JWAAlg.EDDSA:
        # File-based providers commonly store Ed25519 keys in PEM format. The
        # Ed25519 signer expects raw 32/64-byte seed material, so convert when
        # necessary.
        if mat.startswith(b"-----BEGIN"):
            from cryptography.hazmat.primitives import serialization

            priv = serialization.load_pem_private_key(mat, password=None)
            mat = priv.private_bytes(
                serialization.Encoding.Raw,
                serialization.PrivateFormat.Raw,
                serialization.NoEncryption(),
            )
        return {"kind": "raw_ed25519_sk", "bytes": mat}
    if alg == JWAAlg.HS256:
        return {"kind": "raw", "key": mat}
    # RSA/ECDSA private keys are provided as PEM bytes
    return {"kind": "pem_priv", "data": mat}


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

        if not kid:
            raise ValueError("mint requires 'kid' of a signing key")
        ref = await self._kp.get_key(kid, key_version, include_secret=True)
        if ref.material is None:
            raise RuntimeError("Signing key is not exportable under current policy")

        headers = dict(headers or {})
        headers.setdefault("kid", f"{ref.kid}.{ref.version}")

        key = _ref_to_signing_key(ref, alg)
        return await self._jws.sign_compact(
            payload=payload,
            alg=alg,
            key=key,
            kid=headers["kid"],
            header_extra={k: v for k, v in headers.items() if k != "kid"},
            typ="JWT",
        )

    async def verify(
        self,
        token: str,
        *,
        issuer: Optional[str] = None,
        audience: Optional[str | list[str]] = None,
        leeway_s: int = 60,
    ) -> Dict[str, Any]:
        jwks = await self._kp.jwks()

        def _resolver(kid: str | None, alg: str) -> dict[str, Any] | None:
            if not kid:
                return None
            for jwk in jwks.get("keys", []):
                if jwk.get("kid") == kid:
                    return jwk
            return None

        res = await self._jws.verify_compact(
            token,
            jwks_resolver=lambda k, a: _resolver(k, a),
            alg_allowlist=self.supports()["algs"],
        )
        payload = json.loads(res.payload.decode("utf-8"))

        now = int(time.time())
        exp = payload.get("exp")
        if exp is not None and now > int(exp) + leeway_s:
            raise ValueError("token is expired")
        nbf = payload.get("nbf")
        if nbf is not None and now + leeway_s < int(nbf):
            raise ValueError("token not yet valid")
        iss_expected = issuer or self._iss
        if iss_expected and payload.get("iss") != iss_expected:
            raise ValueError("invalid issuer")
        if audience is not None:
            aud_claim = payload.get("aud")
            if isinstance(aud_claim, list):
                if audience not in aud_claim:
                    raise ValueError("invalid audience")
            elif aud_claim != audience:
                raise ValueError("invalid audience")
        return payload

    async def jwks(self) -> dict:
        return await self._kp.jwks()
