"""Tests for RFC 9449 compliance of :class:`DPoPBoundJWTTokenService`."""

import base64
import time
from typing import Dict, Optional
from uuid import uuid4

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from swarmauri_core.crypto.types import (
    ExportPolicy,
    JWAAlg,
    KeyRef,
    KeyType,
    KeyUse,
)
from swarmauri_core.keys.IKeyProvider import IKeyProvider

from swarmauri_tokens_dpopboundjwt import (
    DPoPBoundJWTTokenService,
    jwk_thumbprint_sha256,
)

RFC9449_SPEC = """
Section 4 of RFC 9449 states that a DPoP proof JWT MUST:
  * contain the JOSE header parameter "typ" with value "dpop+jwt";
  * include the claims "htm", "htu", "iat", and "jti";
  * be signed with the public key described by the "jwk" header
    parameter and the access token's "cnf.jkt" must match the
    JWK thumbprint of that key.
"""


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


class StaticKeyProvider(IKeyProvider):
    """Minimal symmetric key provider for tests."""

    def __init__(self, secret: bytes) -> None:
        self._secret = secret

    def supports(self) -> Dict[str, list[str]]:
        return {"algs": [JWAAlg.HS256.value]}

    async def create_key(self, spec):
        raise NotImplementedError

    async def import_key(self, spec, material, *, public=None):
        raise NotImplementedError

    async def rotate_key(self, kid: str, *, spec_overrides: Optional[dict] = None):
        raise NotImplementedError

    async def destroy_key(self, kid: str, version: Optional[int] = None) -> bool:
        raise NotImplementedError

    async def get_key(
        self, kid: str, version: Optional[int] = None, *, include_secret: bool = False
    ) -> KeyRef:
        return KeyRef(
            kid=kid,
            version=1,
            type=KeyType.SYMMETRIC,
            uses=(KeyUse.SIGN,),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            material=self._secret,
        )

    async def list_versions(self, kid: str):
        return (1,)

    async def get_public_jwk(self, kid: str, version: Optional[int] = None) -> dict:
        return {"kty": "oct", "k": _b64u(self._secret)}

    async def jwks(self, *, prefix_kids: Optional[str] = None) -> dict:
        raise NotImplementedError

    async def random_bytes(self, n: int) -> bytes:
        raise NotImplementedError

    async def hkdf(self, ikm: bytes, *, salt: bytes, info: bytes, length: int) -> bytes:
        raise NotImplementedError


async def _mint_token(
    ctx: Dict[str, object],
) -> tuple[DPoPBoundJWTTokenService, str, dict]:
    provider = StaticKeyProvider(b"secret")
    svc = DPoPBoundJWTTokenService(provider, dpop_ctx_getter=lambda: ctx)

    sk = ed25519.Ed25519PrivateKey.generate()
    pk = sk.public_key()
    pub = pk.public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
    )
    jwk = {"kty": "OKP", "crv": "Ed25519", "x": _b64u(pub)}
    ctx["jwk"] = jwk
    token = await svc.mint({}, alg=JWAAlg.HS256)
    del ctx["jwk"]
    return svc, token, {"sk": sk, "jwk": jwk}


@pytest.mark.asyncio
async def test_valid_dpop_proof() -> None:
    """A well-formed DPoP proof passes verification."""

    ctx: Dict[str, object] = {}
    svc, token, extras = await _mint_token(ctx)
    now = int(time.time())
    payload = {
        "htu": "https://api.example.com/resource",
        "htm": "GET",
        "iat": now,
        "jti": str(uuid4()),
    }
    proof = jwt.encode(
        payload,
        extras["sk"],
        algorithm="EdDSA",
        headers={"jwk": extras["jwk"], "typ": "dpop+jwt"},
    )
    ctx.update(
        {"proof": proof, "htm": "GET", "htu": "https://api.example.com/resource"}
    )
    out = await svc.verify(token)
    assert out["cnf"]["jkt"] == jwk_thumbprint_sha256(extras["jwk"])


@pytest.mark.asyncio
async def test_missing_jti_raises() -> None:
    """Proofs without the required ``jti`` claim are rejected."""

    ctx: Dict[str, object] = {}
    svc, token, extras = await _mint_token(ctx)
    now = int(time.time())
    payload = {
        "htu": "https://api.example.com/resource",
        "htm": "GET",
        "iat": now,
    }  # missing jti
    proof = jwt.encode(
        payload,
        extras["sk"],
        algorithm="EdDSA",
        headers={"jwk": extras["jwk"], "typ": "dpop+jwt"},
    )
    ctx.update(
        {"proof": proof, "htm": "GET", "htu": "https://api.example.com/resource"}
    )
    with pytest.raises(ValueError):
        await svc.verify(token)


@pytest.mark.asyncio
async def test_wrong_typ_raises() -> None:
    """Header ``typ`` other than ``dpop+jwt`` is invalid."""

    ctx: Dict[str, object] = {}
    svc, token, extras = await _mint_token(ctx)
    now = int(time.time())
    payload = {
        "htu": "https://api.example.com/resource",
        "htm": "GET",
        "iat": now,
        "jti": str(uuid4()),
    }
    proof = jwt.encode(
        payload,
        extras["sk"],
        algorithm="EdDSA",
        headers={"jwk": extras["jwk"], "typ": "JWT"},
    )
    ctx.update(
        {"proof": proof, "htm": "GET", "htu": "https://api.example.com/resource"}
    )
    with pytest.raises(ValueError):
        await svc.verify(token)


@pytest.mark.asyncio
async def test_enforcement_can_be_disabled() -> None:
    """DPoP verification can be disabled for non-DPoP flows."""

    provider = StaticKeyProvider(b"secret")
    svc = DPoPBoundJWTTokenService(provider, enforce_proof=False)
    token = await svc.mint({}, alg=JWAAlg.HS256)
    # No context or proof is required when enforcement is off
    out = await svc.verify(token)
    assert "iat" in out and "exp" in out
