![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_keyprovider_local/"><img src="https://img.shields.io/pypi/dm/swarmauri_keyprovider_local" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_keyprovider_local/"><img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_keyprovider_local.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_local/"><img src="https://img.shields.io/pypi/pyversions/swarmauri_keyprovider_local" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_local/"><img src="https://img.shields.io/pypi/l/swarmauri_keyprovider_local" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_local/"><img src="https://img.shields.io/pypi/v/swarmauri_keyprovider_local?label=swarmauri_keyprovider_local&color=green" alt="PyPI - swarmauri_keyprovider_local"/></a>
</p>

# Swarmauri Local Key Provider

Provides a pure in-memory implementation of the `KeyProviderBase` suitable for
local development, unit testing, and rapid prototyping without any external
infrastructure.

## Capabilities

- Generate symmetric AES-256-GCM keys and several asymmetric algorithms
  (Ed25519, X25519, RSA-OAEP/PSS-SHA256, and ECDSA P-256-SHA256).
- Import existing key material and rotate to new versions on demand.
- Retrieve stored keys (optionally including the secret material) and list
  available versions.
- Export public material as individual JWKs or aggregate JWKS documents.
- Produce cryptographically secure random bytes or derive material using HKDF.
- Destroy keys when they are no longer needed to keep local environments tidy.

## Installation

Choose the tool that best matches your workflow:

```bash
# pip
pip install swarmauri_keyprovider_local

# Poetry
poetry add swarmauri_keyprovider_local

# uv
uv add swarmauri_keyprovider_local
```

## Quickstart

The example below mirrors `swarmauri_keyprovider_local.examples.basic_usage`
and demonstrates how to create, store, and retrieve a symmetric key.

```python
import asyncio
from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_core.keys.types import (
    ExportPolicy,
    KeyAlg,
    KeyClass,
    KeySpec,
)
from swarmauri_core.crypto.types import KeyUse


async def run_example() -> str:
    """Create and retrieve a symmetric key using LocalKeyProvider."""

    provider = LocalKeyProvider()
    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,
        uses=(KeyUse.ENCRYPT,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    created = await provider.create_key(spec)
    fetched = await provider.get_key(created.kid, include_secret=True)
    assert fetched.material is not None
    return fetched.kid


if __name__ == "__main__":
    print(asyncio.run(run_example()))
```

### Rotate, export, and derive

Once you have a provider instance, additional asynchronous helpers are
available to manage keys and metadata:

```python
# Rotate the current key in-place (keeps the same KID with a new version)
rotated = await provider.rotate_key(created.kid)

# List available versions for auditing or debugging
versions = await provider.list_versions(created.kid)

# Export public material
jwk = await provider.get_public_jwk(created.kid)
jwks = await provider.jwks()

# Destroy keys when finished
await provider.destroy_key(created.kid)

# Generate bytes or derive new material locally
random_bytes = await provider.random_bytes(32)
derived = await provider.hkdf(b"ikm", salt=b"salt", info=b"context", length=32)
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.