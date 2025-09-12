"""JWT token service implementation.

Provides the :class:`JWTTokenService` for minting and verifying JSON Web
Tokens (JWT) using keys supplied by an :class:`~swarmauri_core.keys.IKeyProvider`.
"""

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
    """Convert a key reference into a signer/verifier mapping.

    ref (KeyRef): Reference containing the signing material.
    alg (JWAAlg): Algorithm used to sign the token.

    RETURNS (Mapping[str, Any]): Key specification understood by
        :class:`~swarmauri_signing_jws.JwsSignerVerifier`.

    RAISES (RuntimeError): If signing material is not available.
    """

    mat = ref.material
    if mat is None:
        raise RuntimeError("key material not available for signing")
    if alg == JWAAlg.EDDSA:
        if isinstance(mat, (bytes, bytearray)) and mat.startswith(b"-----BEGIN"):
            from cryptography.hazmat.primitives import serialization

            key_obj = serialization.load_pem_private_key(mat, password=None)
            return {"kind": "cryptography_obj", "obj": key_obj}
        return {"kind": "raw_ed25519_sk", "bytes": mat}
    if alg == JWAAlg.HS256:
        return {"kind": "raw", "key": mat}
    # RSA/ECDSA private keys are provided as PEM bytes
    return {"kind": "pem_priv", "data": mat}


class JWTTokenService(TokenServiceBase):
    """JWS/JWT issuer and verifier backed by a key provider.

    key_provider (IKeyProvider): Source of signing keys.
    default_issuer (str): Default issuer claim for minted tokens.
    """

    type: Literal["JWTTokenService"] = "JWTTokenService"

    def __init__(
        self, key_provider: IKeyProvider, *, default_issuer: Optional[str] = None
    ) -> None:
        """Initialize the token service.

        key_provider (IKeyProvider): Provider used to fetch signing keys.
        default_issuer (str): Optional issuer applied when minting tokens.
        """

        super().__init__()
        self._kp = key_provider
        self._iss = default_issuer
        self._jws = JwsSignerVerifier()

    def supports(self) -> Mapping[str, Iterable[JWAAlg]]:
        """Describe supported formats and algorithms.

        RETURNS (Mapping[str, Iterable[JWAAlg]]): Supported formats and
            algorithms for minting and verification.
        """

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
        """Mint a signed JWT.

        claims (Dict[str, Any]): Claims to embed in the token.
        alg (JWAAlg): Signing algorithm.
        kid (str): Identifier of the signing key.
        key_version (int): Optional version of the signing key.
        headers (Dict[str, Any]): Extra protected headers.
        lifetime_s (int): Token lifetime in seconds.
        issuer (str): Issuer claim to include.
        subject (str): Subject claim to include.
        audience (str or list[str]): Audience claim.
        scope (str): Scope claim.

        RETURNS (str): Encoded JWT string.

        RAISES (ValueError): If no ``kid`` is provided.
        RAISES (RuntimeError): If signing key material cannot be exported.
        """

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
        """Verify a JWT and return its claims.

        token (str): Encoded JWT to verify.
        issuer (str): Expected issuer claim.
        audience (str or list[str]): Expected audience claim.
        leeway_s (int): Allowed clock skew in seconds.

        RETURNS (Dict[str, Any]): Verified token claims.

        RAISES (ValueError): If token is invalid or verification fails.
        """

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
        """Return the JSON Web Key Set for public key discovery.

        RETURNS (dict): JWKS document containing available public keys.
        """

        return await self._kp.jwks()
