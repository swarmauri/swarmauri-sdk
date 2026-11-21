# README example: mint and verify a DPoP-bound JWT
import asyncio
import json
import os
import time
import uuid
from typing import Any, Iterable, Mapping, Optional

import jwt
from cryptography.hazmat.primitives.asymmetric import ec
from jwt import algorithms

from swarmauri_core.crypto.types import (
    ExportPolicy,
    JWAAlg,
    KeyRef,
    KeyType,
    KeyUse,
)
from swarmauri_core.key_providers.IKeyProvider import IKeyProvider
from swarmauri_tokens_dpopboundjwt import DPoPBoundJWTTokenService


class StaticKeyProvider(IKeyProvider):
    """Minimal symmetric key provider suitable for examples/tests."""

    def __init__(self, secret: bytes, kid: str = "default") -> None:
        self._kid = kid
        self._secret = secret
        self._ref = KeyRef(
            kid=kid,
            version=1,
            type=KeyType.SYMMETRIC,
            uses=(KeyUse.SIGN, KeyUse.VERIFY),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            material=secret,
        )

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {"algs": ("HS256",)}

    async def create_key(
        self, spec: Any
    ):  # pragma: no cover - unused in example
        raise NotImplementedError

    async def import_key(
        self, spec: Any, material: bytes, *, public: bytes | None = None
    ):  # pragma: no cover - unused in example
        raise NotImplementedError

    async def rotate_key(
        self, kid: str, *, spec_overrides: Optional[dict] = None
    ):  # pragma: no cover - unused in example
        raise NotImplementedError

    async def destroy_key(
        self, kid: str, version: Optional[int] = None
    ) -> bool:  # pragma: no cover - unused in example
        return False

    async def get_key(
        self,
        kid: str,
        version: Optional[int] = None,
        *,
        include_secret: bool = False,
    ) -> KeyRef:
        return self._ref

    async def list_versions(
        self, kid: str
    ) -> tuple[int, ...]:  # pragma: no cover
        return (self._ref.version,)

    async def get_public_jwk(  # pragma: no cover - unused in example
        self, kid: str, version: Optional[int] = None
    ) -> dict:
        raise NotImplementedError

    async def jwks(  # pragma: no cover - unused in example
        self, *, prefix_kids: Optional[str] = None
    ) -> dict:
        raise NotImplementedError

    async def random_bytes(self, n: int) -> bytes:  # pragma: no cover - unused
        return os.urandom(n)

    async def hkdf(  # pragma: no cover - unused in example
        self, ikm: bytes, *, salt: bytes, info: bytes, length: int
    ) -> bytes:
        raise NotImplementedError


async def main() -> None:
    key_provider = StaticKeyProvider(b"super-secret-signing-key")
    request_context: dict[str, object] = {}

    def get_ctx() -> dict[str, object]:
        return request_context

    service = DPoPBoundJWTTokenService(
        key_provider,
        default_issuer="https://issuer.test",
        dpop_ctx_getter=get_ctx,
        proof_max_age_s=300,
    )

    # Client presents the public key when the token is minted so we can bind cnf.jkt
    dpop_private_key = ec.generate_private_key(ec.SECP256R1())
    jwk_public = json.loads(
        algorithms.ECAlgorithm.to_jwk(dpop_private_key.public_key())
    )

    request_context.update({"jwk": jwk_public})

    access_token = await service.mint(
        {"sub": "alice@example.com"},
        alg=JWAAlg.HS256,
        audience="https://api.example.test",
        scope="read:messages",
    )

    # Incoming request carries a DPoP proof signed with the same key material
    htu = "https://api.example.test/resource"
    htm = "GET"
    nonce = "server-provided-nonce"
    proof_claims = {
        "htu": htu,
        "htm": htm,
        "iat": int(time.time()),
        "jti": str(uuid.uuid4()),
        "nonce": nonce,
    }
    proof_headers = {"typ": "dpop+jwt", "jwk": jwk_public}
    proof_jwt = jwt.encode(
        proof_claims,
        dpop_private_key,
        algorithm="ES256",
        headers=proof_headers,
    )

    request_context.update(
        {
            "proof": proof_jwt,
            "htu": htu,
            "htm": htm,
            "nonce": nonce,
        }
    )

    verified_claims = await service.verify(
        access_token, audience="https://api.example.test"
    )
    print("Verified subject:", verified_claims["sub"])
    print("Bound JWK thumbprint:", verified_claims["cnf"]["jkt"])


if __name__ == "__main__":
    asyncio.run(main())
