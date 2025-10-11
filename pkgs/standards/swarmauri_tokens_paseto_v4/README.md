![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_tokens_paseto_v4/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tokens_paseto_v4" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tokens_paseto_v4/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tokens_paseto_v4.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_paseto_v4/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tokens_paseto_v4" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_paseto_v4/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tokens_paseto_v4" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_paseto_v4/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tokens_paseto_v4?label=swarmauri_tokens_paseto_v4&color=green" alt="PyPI - swarmauri_tokens_paseto_v4"/></a>
</p>

---

# Swarmauri Token Paseto V4

`PasetoV4TokenService` provides `v4.public` signing and `v4.local`
encryption for Swarmauri-compatible applications using the
[`pyseto`](https://pypi.org/project/pyseto/) reference implementation.  The
service implements the `ITokenService` interface and validates standard JWT
claims (`exp`, `nbf`, `iat`, `iss`, and `aud`) when verifying tokens.

## Features

- Ed25519 signing for `v4.public` operations using keys supplied by an
  `IKeyProvider` implementation.
- XChaCha20-Poly1305 encryption for `v4.local` tokens with symmetric keys.
- Automatic population of `iat` and `nbf` claims plus an optional `exp`
  derived from `lifetime_s`.
- Registered-claim validation during verification with configurable issuer and
  audience matching.
- Optional CBOR canonicalization of payloads via the `cbor` extra.
- Asynchronous API compatible with the broader Swarmauri token service
  ecosystem.

## Installation

Install the package with your preferred Python packaging tool:

```bash
pip install swarmauri_tokens_paseto_v4
```

```bash
poetry add swarmauri_tokens_paseto_v4
```

```bash
uv pip install swarmauri_tokens_paseto_v4
```

## Key provider requirements

`PasetoV4TokenService` delegates key management to an object implementing the
`IKeyProvider` interface from `swarmauri_core`.  The provider is expected to:

- Return an Ed25519 private key (PEM encoded) when `get_key` is called for
  `v4.public` signing operations.
- Return a 32-byte symmetric key for `v4.local` encryption and expose the
  corresponding key IDs through the service's `local_kids` parameter.
- Supply an Ed25519 JWK via `jwks()` so that public tokens can be verified
  without direct access to the signing key material.
- Optionally provide a default issuer, implicit assertions, and key rotation
  metadata using the `KeyRef` structure from `swarmauri_core`.

## Claim handling

When minting a token the service merges your custom claim payload with a set of
registered defaults:

- `iat` (issued at) and `nbf` (not before) are populated with the current epoch
  time when not explicitly provided.
- `exp` (expiration) is derived from `lifetime_s` when supplied.
- `iss`, `sub`, `aud`, and `scope` claims are added when the corresponding
  keyword arguments are passed to `mint` or when a `default_issuer` is set on
  the service instance.

During verification the service ensures that tokens are not expired, are
currently valid, and that issuer and audience claims match the expectations you
supply.

## Usage

The example below spins up an in-memory key provider with one Ed25519 signing
key and one symmetric key, mints both `v4.public` and `v4.local` tokens, and
verifies their contents.

```python
import asyncio
import base64
import os
from typing import Iterable, Mapping, Optional

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

from swarmauri_tokens_paseto_v4 import PasetoV4TokenService
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse
from swarmauri_core.key_providers.IKeyProvider import IKeyProvider
from swarmauri_core.key_providers.types import KeyAlg


class InMemoryKeyProvider(IKeyProvider):
    def __init__(self) -> None:
        self._sk = Ed25519PrivateKey.generate()
        self._sym = os.urandom(32)
        self._refs = {
            "ed1": KeyRef(
                kid="ed1",
                version=1,
                type=KeyType.ED25519,
                uses=(KeyUse.SIGN, KeyUse.VERIFY),
                export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
                material=self._sk.private_bytes(
                    Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()
                ),
                public=self._sk.public_key().public_bytes(
                    Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
                ),
                tags={"alg": KeyAlg.ED25519.value},
            ),
            "sym1": KeyRef(
                kid="sym1",
                version=1,
                type=KeyType.SYMMETRIC,
                uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
                export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
                material=self._sym,
                public=None,
                tags={"alg": KeyAlg.AES256_GCM.value},
            ),
        }
        self._jwks = {
            "keys": [
                {
                    "kty": "OKP",
                    "crv": "Ed25519",
                    "kid": "ed1",
                    "x": base64.urlsafe_b64encode(
                        self._sk.public_key().public_bytes(
                            Encoding.Raw, PublicFormat.Raw
                        )
                    )
                    .rstrip(b"=")
                    .decode("ascii"),
                }
            ]
        }

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {}

    async def create_key(self, spec):  # pragma: no cover - unused in the example
        raise NotImplementedError

    async def import_key(self, spec, material, *, public=None):  # pragma: no cover
        raise NotImplementedError

    async def rotate_key(self, kid, *, spec_overrides=None):  # pragma: no cover
        raise NotImplementedError

    async def destroy_key(self, kid, version=None):  # pragma: no cover
        raise NotImplementedError

    async def get_key(self, kid, version=None, include_secret=False):
        return self._refs[kid]

    async def list_versions(self, kid):  # pragma: no cover - unused
        return (1,)

    async def get_public_jwk(self, kid, version=None):  # pragma: no cover
        return self._jwks["keys"][0]

    async def jwks(self, *, prefix_kids: Optional[str] = None):
        return self._jwks

    async def random_bytes(self, n: int) -> bytes:  # pragma: no cover - unused
        return os.urandom(n)

    async def hkdf(
        self, ikm: bytes, *, salt: bytes, info: bytes, length: int
    ) -> bytes:  # pragma: no cover - unused
        return HKDF(algorithm=hashes.SHA256(), length=length, salt=salt, info=info).derive(ikm)


async def main() -> None:
    provider = InMemoryKeyProvider()
    service = PasetoV4TokenService(
        provider,
        default_issuer="auth.example",
        local_kids=["sym1"],
    )

    public_token = await service.mint(
        {"role": "admin"},
        alg="v4.public",
        kid="ed1",
        audience="my-service",
    )
    verified_public = await service.verify(public_token, audience="my-service")
    print("Verified role:", verified_public["role"])

    local_token = await service.mint(
        {"feature": "beta"},
        alg="v4.local",
        kid="sym1",
    )
    verified_local = await service.verify(local_token)
    print("Local feature flag:", verified_local["feature"])


if __name__ == "__main__":
    asyncio.run(main())
```

Running the script prints the verified claim values for both the signed and the
encrypted token.  In a production deployment you would connect the token
service to your own `IKeyProvider` implementation so the keys can be rotated or
backed by a hardware security module.

## Entry points

The package exposes `PasetoV4TokenService` under the `swarmauri.tokens`
setuptools entry point group, making it discoverable by other Swarmauri
components.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.