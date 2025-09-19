![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_tokens_dpopboundjwt/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tokens_dpopboundjwt" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tokens_dpopboundjwt/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tokens_dpopboundjwt.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_dpopboundjwt/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tokens_dpopboundjwt" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_dpopboundjwt/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tokens_dpopboundjwt" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_dpopboundjwt/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tokens_dpopboundjwt?label=swarmauri_tokens_dpopboundjwt&color=green" alt="PyPI - swarmauri_tokens_dpopboundjwt"/></a>
</p>

---

# Swarmauri Tokens DPoP Bound JWT

DPoP-bound JSON Web Token (JWT) services for Swarmauri implementing [RFC 9449](https://www.rfc-editor.org/rfc/rfc9449) DPoP proof binding and [RFC 7638](https://www.rfc-editor.org/rfc/rfc7638) JWK thumbprints.

## Features

- Mints and verifies DPoP-bound JWT access tokens using the algorithms provided by the base `JWTTokenService` (`HS256`, `RS256`, `PS256`, `ES256`, `EdDSA`).
- Automatically injects the RFC 7638 thumbprint into the `cnf.jkt` claim when the DPoP context exposes the caller's public JWK.
- Enforces DPoP proof validation by checking the `dpop+jwt` header type, verifying the proof signature against the embedded JWK, and binding the HTTP method/URI, `iat`, and optional nonce (`proof_max_age_s` controls the allowed clock skew).
- Accepts an optional `replay_check(jti)` callback to harden against proof re-use and a `dpop_ctx_getter` to integrate with request-scoped metadata providers.
- Compatible with the `JWTTokenService` surface for issuer, subject, audience, scope, key selection, and header overrides.

## Installation

### pip

```bash
pip install swarmauri_tokens_dpopboundjwt
```

### uv

```bash
uv add swarmauri_tokens_dpopboundjwt
```

### Poetry

```bash
poetry add swarmauri_tokens_dpopboundjwt
```

## Usage

### DPoP context expectations

`DPoPBoundJWTTokenService` extends `JWTTokenService` and requires request context in order to bind and verify DPoP proofs. Supply a callable via `dpop_ctx_getter` that returns a mapping with the following keys:

- `jwk`: optional public JWK exposed during minting to automatically populate `cnf.jkt`.
- `proof`: the DPoP proof JWT received with a request.
- `htm`: HTTP method used for the protected resource request.
- `htu`: absolute HTTP URI for the protected resource request.
- `nonce`: optional server-provided nonce that, when present, must match the proof.

Set `enforce_proof=False` only when you intentionally want to accept tokens without a proof (for example during incremental rollout).

### Example: mint and verify a DPoP-bound JWT

```python
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
from swarmauri_core.keys.IKeyProvider import IKeyProvider
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

    async def create_key(self, spec: Any):  # pragma: no cover - unused in example
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
        self, kid: str, version: Optional[int] = None, *, include_secret: bool = False
    ) -> KeyRef:
        return self._ref

    async def list_versions(self, kid: str) -> tuple[int, ...]:  # pragma: no cover
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
    jwk_public = json.loads(algorithms.ECAlgorithm.to_jwk(dpop_private_key.public_key()))

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
        proof_claims, dpop_private_key, algorithm="ES256", headers=proof_headers
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
```

## Entry Point

The service registers under the `swarmauri.tokens` entry point as `DPoPBoundJWTTokenService`.

A plain `JWTTokenService` is also exported for cases where DPoP binding is not required.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.