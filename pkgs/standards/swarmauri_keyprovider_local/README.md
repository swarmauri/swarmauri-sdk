![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_keyprovider_local/"><img src="https://img.shields.io/pypi/dm/swarmauri_keyprovider_local" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_keyprovider_local/"><img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_keyprovider_local.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_local/"><img src="https://img.shields.io/pypi/pyversions/swarmauri_keyprovider_local" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_local/"><img src="https://img.shields.io/pypi/l/swarmauri_keyprovider_local" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_local/"><img src="https://img.shields.io/pypi/v/swarmauri_keyprovider_local?label=swarmauri_keyprovider_local&color=green" alt="PyPI - swarmauri_keyprovider_local"/></a>
</p>

# Swarmauri Local Key Provider

Provides a simple in-memory key provider for development and testing.

## Features

- Supports AES-256-GCM, Ed25519, X25519, RSA, and ECDSA algorithms.
- Pure in-memory storage ideal for tests and local development.
- Import existing keys and rotate through multiple versions.
- Export public keys as JWK or JWKS documents.
- Generate random bytes or derive material with HKDF.

## Installation

```bash
pip install swarmauri_keyprovider_local
```

## Usage

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
    provider = LocalKeyProvider()
    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,
        uses=(KeyUse.ENCRYPT,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    created = await provider.create_key(spec)
    fetched = await provider.get_key(created.kid, include_secret=True)
    print(f"Retrieved key: {fetched.kid}")


asyncio.run(run_example())
```

Keys may be rotated and exported as a JWKS:

```python
rotated = await provider.rotate_key(created.kid)
jwks = await provider.jwks()
```
