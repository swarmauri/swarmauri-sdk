import asyncio
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

from swarmauri_tokens_dpopboundjwt import DPoPBoundJWTTokenService


def _b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")


class StaticKeyProvider(IKeyProvider):
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


@pytest.mark.perf
def test_verify_perf(benchmark) -> None:
    ctx: Dict[str, object] = {}
    provider = StaticKeyProvider(b"secret")
    svc = DPoPBoundJWTTokenService(provider, dpop_ctx_getter=lambda: ctx)

    sk = ed25519.Ed25519PrivateKey.generate()
    pk = sk.public_key()
    pub = pk.public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
    )
    jwk = {"kty": "OKP", "crv": "Ed25519", "x": _b64u(pub)}

    ctx["jwk"] = jwk
    token = asyncio.run(svc.mint({}, alg=JWAAlg.HS256))
    del ctx["jwk"]

    now = int(time.time())
    proof_payload = {
        "htu": "https://api.example.com/resource",
        "htm": "GET",
        "iat": now,
        "jti": str(uuid4()),
    }
    proof = jwt.encode(
        proof_payload, sk, algorithm="EdDSA", headers={"jwk": jwk, "typ": "dpop+jwt"}
    )
    ctx.update(
        {"proof": proof, "htm": "GET", "htu": "https://api.example.com/resource"}
    )

    def _verify() -> None:
        asyncio.run(svc.verify(token))

    benchmark(_verify)
