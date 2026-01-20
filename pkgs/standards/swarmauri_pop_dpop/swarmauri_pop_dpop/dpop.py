from __future__ import annotations

import binascii
import json
from typing import Mapping, Optional

import jwt
from jwt import InvalidTokenError
from jwt.algorithms import get_default_algorithms
from jwt.utils import base64url_decode

from swarmauri_core.pop import (
    BindType,
    CnfBinding,
    Feature,
    PoPBindingError,
    PoPParseError,
    PoPVerificationError,
    PoPKind,
)
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.pop import (
    PopSigningBase,
    PopVerifierBase,
    RequestContext,
    sha256_b64u,
)


def _compute_jwk_thumbprint(jwk: Mapping[str, object]) -> str:
    try:
        kty = jwk["kty"]
    except KeyError as exc:
        raise PoPParseError("JWK missing kty") from exc

    if kty == "EC":
        fields = {"crv": jwk["crv"], "kty": "EC", "x": jwk["x"], "y": jwk["y"]}
    elif kty == "RSA":
        fields = {"e": jwk["e"], "kty": "RSA", "n": jwk["n"]}
    elif kty == "OKP":
        fields = {"crv": jwk["crv"], "kty": "OKP", "x": jwk["x"]}
    else:
        raise PoPParseError(f"Unsupported JWK kty '{kty}' for thumbprint")

    canonical = json.dumps(fields, separators=(",", ":"), sort_keys=True).encode(
        "utf-8"
    )
    return sha256_b64u(canonical)


def _resolve_kid(kid: Optional[str]) -> Optional[bytes]:
    if kid is None:
        return None
    return kid.encode("utf-8")


def _parse_unverified_header(proof: str) -> Mapping[str, object]:
    try:
        parts = proof.split(".", maxsplit=2)
    except (AttributeError, ValueError) as exc:
        raise PoPParseError("DPoP header could not be parsed") from exc

    if len(parts) != 3:
        raise PoPParseError("DPoP header could not be parsed")

    header_segment = parts[0]

    try:
        header_bytes = base64url_decode(header_segment.encode("utf-8"))
        header = json.loads(header_bytes)
    except (TypeError, binascii.Error, json.JSONDecodeError) as exc:
        raise PoPParseError("DPoP header could not be parsed") from exc

    if not isinstance(header, Mapping):
        raise PoPParseError("DPoP header could not be parsed")
    return header


@ComponentBase.register_type(PopVerifierBase, "DPoPVerifier")
class DPoPVerifier(PopVerifierBase):
    """Verifier for RFC 9449 DPoP proofs."""

    def __init__(self) -> None:
        super().__init__(
            kind=PoPKind.JWT_DPoP,
            header_name="DPoP",
            features=Feature.NONCE | Feature.REPLAY | Feature.ATH,
            algorithms=("ES256", "EdDSA", "PS256"),
        )

    async def _verify_core(
        self,
        proof: str,
        context: RequestContext,
        cnf: CnfBinding,
        *,
        replay,
        keys,
        extras,
    ) -> None:
        self._enforce_bind_type(cnf, context.policy, expected=BindType.JKT)

        header = _parse_unverified_header(proof)

        alg = header.get("alg")
        if not isinstance(alg, str):
            raise PoPParseError("DPoP header missing alg")
        self._enforce_alg_policy(alg, context.policy)

        jwk_header = header.get("jwk")
        kid = header.get("kid")

        key_obj = None
        thumbprint = None

        if isinstance(jwk_header, Mapping):
            thumbprint = _compute_jwk_thumbprint(jwk_header)
            if thumbprint != cnf.value_b64u:
                raise PoPBindingError(
                    "Proof key thumbprint does not match access token cnf"
                )
            alg_impl = get_default_algorithms().get(alg)
            if alg_impl is None:
                raise PoPVerificationError(f"Unsupported algorithm {alg}")
            key_obj = alg_impl.from_jwk(json.dumps(jwk_header))
        else:
            if keys is None:
                raise PoPVerificationError(
                    "Key resolver required when proof omits public JWK"
                )
            kid_bytes = _resolve_kid(kid)
            key_obj = None
            if kid_bytes is not None:
                key_obj = keys.by_kid(kid_bytes)
            if key_obj is None:
                key_obj = keys.by_thumb(cnf)
            if key_obj is None:
                raise PoPVerificationError("No verification key available for proof")

        options = {
            "verify_aud": False,
            "verify_exp": False,
            "verify_iat": False,
            "verify_iss": False,
            "require": ["htm", "htu", "iat"],
        }

        try:
            payload = jwt.decode(proof, key_obj, algorithms=[alg], options=options)
        except InvalidTokenError as exc:
            raise PoPVerificationError("DPoP signature verification failed") from exc

        if payload.get("htm") != context.method or payload.get("htu") != context.htu:
            raise PoPVerificationError("DPoP htm/htu mismatch")

        try:
            iat = int(payload["iat"])
        except (KeyError, ValueError, TypeError) as exc:
            raise PoPParseError("Invalid or missing iat claim") from exc
        self._validate_iat(iat, context.policy)

        jti = payload.get("jti")
        if not isinstance(jti, str) or not jti:
            raise PoPParseError("Missing jti claim")

        nonce_expected = extras.get("nonce")
        nonce_claim = payload.get("nonce")
        if nonce_expected is not None and nonce_claim != nonce_expected:
            raise PoPVerificationError("Nonce mismatch")

        ath_claim = payload.get("ath")
        if context.policy.require_ath:
            self._require_ath(ath_claim=ath_claim, policy=context.policy, extras=extras)
        elif ath_claim and "access_token" in extras:
            expected_ath = self._compute_ath(extras["access_token"])
            if expected_ath != ath_claim:
                raise PoPVerificationError(
                    "ath claim does not match provided access token"
                )

        replay_scope = f"dpop:{context.htu}"
        self._check_replay(
            replay=replay,
            scope=replay_scope,
            key=jti,
            ttl_s=context.policy.max_skew_s,
        )


@ComponentBase.register_type(PopSigningBase, "DPoPSigner")
class DPoPSigner(PopSigningBase):
    """Signer that emits `dpop+jwt` proofs."""

    def __init__(
        self,
        *,
        private_key,
        public_jwk: Mapping[str, object],
        algorithm: str,
        include_query: bool = False,
    ) -> None:
        super().__init__(
            kind=PoPKind.JWT_DPoP, header_name="DPoP", include_query=include_query
        )
        self._private_key = private_key
        self._public_jwk = dict(public_jwk)
        self._algorithm = algorithm
        self._thumbprint = _compute_jwk_thumbprint(self._public_jwk)

    def cnf_binding(self) -> CnfBinding:
        return CnfBinding(BindType.JKT, self._thumbprint)

    def sign_request(
        self,
        method: str,
        url: str,
        *,
        kid: Optional[bytes] = None,
        jti: Optional[str] = None,
        ath_b64u: Optional[str] = None,
        extra_claims: Mapping[str, object] | None = None,
    ) -> str:
        claims = self._base_claims(method, url, jti=jti, ath_b64u=ath_b64u)
        payload = self._merge_claims(claims, extra_claims)

        headers = {"typ": "dpop+jwt", "jwk": self._public_jwk}
        if kid is not None:
            headers["kid"] = (
                kid.decode("utf-8") if isinstance(kid, (bytes, bytearray)) else str(kid)
            )

        token = jwt.encode(
            payload, self._private_key, algorithm=self._algorithm, headers=headers
        )
        return token
