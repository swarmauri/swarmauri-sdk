![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tokens_jwt/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tokens_jwt" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tokens_jwt/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tokens_jwt.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_jwt/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tokens_jwt" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_jwt/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tokens_jwt" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_jwt/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tokens_jwt?label=swarmauri_tokens_jwt&color=green" alt="PyPI - swarmauri_tokens_jwt"/></a>

</p>

---

# swarmauri_tokens_jwt

A standard JWT token service for the Swarmauri framework. This service
implements minting and verifying JSON Web Tokens and exposes a JWKS
endpoint for public key discovery.

## Installation

Install the service with your preferred Python packaging tool:

```bash
pip install swarmauri_tokens_jwt
```

```bash
poetry add swarmauri_tokens_jwt
```

```bash
uv pip install swarmauri_tokens_jwt
```

## Features

- Mint and verify JWS/JWT tokens backed by any :class:`~swarmauri_core.keys.IKeyProvider`
- Supports algorithms like **HS256**, **RS256**, **ES256**, **PS256** and **EdDSA**
- Adds standard temporal claims (`iat`, `nbf`, and optional `exp`) plus issuer,
  subject, audience and scope defaults when minting tokens
- Validates expiration, not-before, issuer and audience claims during
  verification
- Publishes a JWKS endpoint for public key discovery through your key provider
- Install the optional ``cryptography`` dependency to enable RSA, ECDSA and
  EdDSA signing keys

## Usage

`JWTTokenService` requires an asynchronous `IKeyProvider` to supply signing
material. The example below shows how to mint and verify a symmetric **HS256**
token using a minimal in-memory key provider.

```python
import asyncio
import base64
from swarmauri_tokens_jwt import JWTTokenService
from swarmauri_core.keys import (
    ExportPolicy,
    IKeyProvider,
    KeyRef,
    KeyUse,
)
from swarmauri_core.crypto.types import JWAAlg, KeyType


class InMemoryKeyProvider(IKeyProvider):
    def __init__(self) -> None:
        self.secret = b"secret"
        self.kid = "sym"
        self.version = 1

    def supports(self) -> dict[str, list[str]]:
        return {}

    async def create_key(self, spec):
        raise NotImplementedError

    async def import_key(self, spec, material, *, public=None):
        raise NotImplementedError

    async def rotate_key(self, kid, *, spec_overrides=None):
        raise NotImplementedError

    async def destroy_key(self, kid, version=None) -> bool:
        return False

    async def get_key(self, kid, version=None, *, include_secret=False) -> KeyRef:
        material = self.secret if include_secret else None
        return KeyRef(
            kid=self.kid,
            version=self.version,
            type=KeyType.OPAQUE,
            uses=(KeyUse.SIGN,),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            material=material,
        )

    async def list_versions(self, kid):
        return (self.version,)

    async def get_public_jwk(self, kid, version=None):
        return {}

    async def jwks(self) -> dict:
        k = base64.urlsafe_b64encode(self.secret).rstrip(b"=").decode()
        return {"keys": [{"kty": "oct", "kid": f"{self.kid}.{self.version}", "k": k}]}

    async def random_bytes(self, n: int) -> bytes:
        return b"\x00" * n

    async def hkdf(self, ikm: bytes, *, salt: bytes, info: bytes, length: int) -> bytes:
        return b"\x00" * length


async def main() -> None:
    svc = JWTTokenService(InMemoryKeyProvider(), default_issuer="issuer")
    token = await svc.mint(
        {"sub": "alice"},
        alg=JWAAlg.HS256,
        kid="sym",
        lifetime_s=600,  # override the default one-hour lifetime if needed
    )
    claims = await svc.verify(token, issuer="issuer")
    assert claims["sub"] == "alice"


asyncio.run(main())
```

`verify` retrieves the JSON Web Key Set from the provider and enforces
expiration, not-before, issuer and audience checks before returning the decoded
claims. Expose the service's :meth:`jwks` coroutine to publish the active public
keys from your provider.

The service also supports asymmetric algorithms such as **RS256**, **ES256** and
**EdDSA** when the key provider exposes the appropriate keys. See the
docstrings in :mod:`swarmauri_tokens_jwt` for additional details on the API
surface.
