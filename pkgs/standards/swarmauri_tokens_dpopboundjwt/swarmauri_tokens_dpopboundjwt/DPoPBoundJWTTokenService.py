from __future__ import annotations

import base64
import hashlib
import json
import time
from typing import Callable, Dict, Iterable, Mapping, Optional, Literal

import jwt
from jwt import algorithms

from .JWTTokenService import JWTTokenService
from swarmauri_core.crypto.types import JWAAlg
from swarmauri_core.key_providers.IKeyProvider import IKeyProvider


def _b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")


def jwk_thumbprint_sha256(jwk: Dict[str, object]) -> str:
    """
    RFC 7638 JWK Thumbprint (SHA-256, base64url). We serialize the "required members"
    for the kty family, with lexicographic member order and no whitespace.
    """
    kty = jwk.get("kty")
    if kty == "OKP":
        material = {"crv": jwk["crv"], "kty": "OKP", "x": jwk["x"]}
    elif kty == "EC":
        material = {"crv": jwk["crv"], "kty": "EC", "x": jwk["x"], "y": jwk["y"]}
    elif kty == "RSA":
        material = {"e": jwk["e"], "kty": "RSA", "n": jwk["n"]}
    else:
        raise ValueError("Unsupported JWK kty for thumbprint")
    blob = json.dumps(material, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return _b64u(hashlib.sha256(blob).digest())


class DPoPBoundJWTTokenService(JWTTokenService):
    """
    DPoP-bound JWTs per RFC 9449 using the 'cnf' claim with the JWK thumbprint:
      cnf: { "jkt": "<base64url sha-256 of JWK thumbprint (RFC 7638)>" }

    Verification requires access to the current request's DPoP proof JWT and request
    context (HTTP method + URI, optional nonce). Provide a getter that returns:
        {
          "proof": "<DPoP-Proof-JWT>",
          "htm": "GET",
          "htu": "https://api.example.com/resource",
          "nonce": "<optional server-provided nonce>"
        }
    """

    type: Literal["DPoPBoundJWTTokenService"] = "DPoPBoundJWTTokenService"

    def __init__(
        self,
        key_provider: IKeyProvider,
        *,
        default_issuer: Optional[str] = None,
        dpop_ctx_getter: Optional[Callable[[], Optional[Dict[str, object]]]] = None,
        proof_max_age_s: int = 300,
        replay_check: Optional[Callable[[str], bool]] = None,
        enforce_proof: bool = True,
    ) -> None:
        super().__init__(key_provider, default_issuer=default_issuer)
        self._get_ctx = dpop_ctx_getter
        self._max_age = int(proof_max_age_s)
        # replay_check(jti) should return True if JTI is fresh (i.e., not seen before).
        # If None, replay protection is skipped.
        self._replay_check = replay_check
        # Toggle strict RFC 9449 verification of the DPoP proof.
        self._enforce = enforce_proof

    def supports(self) -> Mapping[str, Iterable[JWAAlg]]:
        base = super().supports()
        return {"formats": (*base["formats"], "JWT"), "algs": base["algs"]}

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
            # If caller wired a context getter that exposes the public JWK (e.g., during token mint),
            # compute jkt automatically. Otherwise require caller to provide claims["cnf"]["jkt"].
            ctx = self._get_ctx() if self._get_ctx else None
            jwk = ctx.get("jwk") if isinstance(ctx, dict) else None
            if isinstance(jwk, dict):
                claims = dict(claims)
                claims["cnf"] = {"jkt": jwk_thumbprint_sha256(jwk)}
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
        jkt = cnf.get("jkt") if isinstance(cnf, dict) else None
        if self._enforce and not jkt:
            raise ValueError("DPoP-bound token missing cnf.jkt")
        if not self._enforce:
            return claims

        if not self._get_ctx:
            raise ValueError("DPoP verification requires a context getter")
        ctx = self._get_ctx() or {}
        proof_jwt = ctx.get("proof")
        htm = ctx.get("htm")
        htu = ctx.get("htu")
        nonce = ctx.get("nonce")

        if (
            not isinstance(proof_jwt, str)
            or not isinstance(htm, str)
            or not isinstance(htu, str)
        ):
            raise ValueError("Missing DPoP context (proof, htm, htu)")

        # 1) Extract JWK from the DPoP proof header and verify the proof signature
        hdr = jwt.get_unverified_header(proof_jwt)
        if hdr.get("typ") != "dpop+jwt":
            raise ValueError("DPoP proof header 'typ' must be 'dpop+jwt'")
        jwk = hdr.get("jwk")
        if not isinstance(jwk, dict):
            raise ValueError("DPoP proof missing 'jwk' in header")
        key = None
        if jwk.get("kty") == "RSA":
            key = algorithms.RSAAlgorithm.from_jwk(jwk)
        elif jwk.get("kty") == "EC":
            key = algorithms.ECAlgorithm.from_jwk(jwk)
        elif jwk.get("kty") == "OKP":
            key = algorithms.OKPAlgorithm.from_jwk(jwk)
        else:
            raise ValueError("Unsupported DPoP JWK kty")

        proof_claims = jwt.decode(
            proof_jwt,
            key=key,
            algorithms=[
                alg.value
                for alg in (JWAAlg.RS256, JWAAlg.PS256, JWAAlg.ES256, JWAAlg.EDDSA)
            ],
            options={"verify_aud": False, "verify_iss": False},
        )

        # 2) Check the JWK thumbprint matches the token's cnf.jkt
        thumb = jwk_thumbprint_sha256(jwk)
        if thumb != jkt:
            raise ValueError("DPoP binding mismatch (cnf.jkt != proof JWK thumbprint)")

        # 3) Validate method, URL, iat, nonce (if present)
        if proof_claims.get("htm") != htm:
            raise ValueError("DPoP proof 'htm' mismatch")
        if proof_claims.get("htu") != htu:
            raise ValueError("DPoP proof 'htu' mismatch")
        iat = int(proof_claims.get("iat", 0))
        now = int(time.time())
        if not (now - self._max_age <= iat <= now + leeway_s):
            raise ValueError("DPoP proof 'iat' out of acceptable window")
        if nonce is not None and proof_claims.get("nonce") != nonce:
            raise ValueError("DPoP proof 'nonce' mismatch")
        jti = proof_claims.get("jti")
        if not isinstance(jti, str):
            raise ValueError("DPoP proof missing 'jti'")

        # 4) Replay protection (optional but recommended): require fresh JTI
        if self._replay_check and not self._replay_check(jti):
            raise ValueError("DPoP proof replay detected")

        return claims
