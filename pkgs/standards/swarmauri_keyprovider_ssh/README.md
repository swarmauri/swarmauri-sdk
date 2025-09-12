![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_keyprovider_ssh/"><img src="https://img.shields.io/pypi/dm/swarmauri_keyprovider_ssh" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_keyprovider_ssh/"><img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_keyprovider_ssh.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_ssh/"><img src="https://img.shields.io/pypi/pyversions/swarmauri_keyprovider_ssh" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_ssh/"><img src="https://img.shields.io/pypi/l/swarmauri_keyprovider_ssh" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_ssh/"><img src="https://img.shields.io/pypi/v/swarmauri_keyprovider_ssh?label=swarmauri_keyprovider_ssh&color=green" alt="PyPI - swarmauri_keyprovider_ssh"/></a>
</p>

# Swarmauri SSH Key Provider

Interfaces with local SSH keys to generate and manage signing keys.

## Features

- Generate Ed25519, RSA-PSS, and ECDSA P-256 key pairs.
- Import existing keys from PEM or OpenSSH formats.
- Rotate keys and track key versions.
- Export public keys as JWK or JWKS documents.
- Produce random bytes or derive material via HKDF.

## Installation

```bash
pip install swarmauri_keyprovider_ssh
```

## Usage

The provider exposes an asynchronous interface for creating and managing
SSH-based signing keys.  The snippet below creates a new Ed25519 key and
exports its public component as a JSON Web Key (JWK):

```python
import asyncio
from swarmauri_keyprovider_ssh import SshKeyProvider
from swarmauri_core.keys.types import (
    KeySpec,
    KeyAlg,
    KeyClass,
    ExportPolicy,
    KeyUse,
)


async def main() -> None:
    provider = SshKeyProvider()
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        uses=(KeyUse.SIGN, KeyUse.VERIFY),
        export_policy=ExportPolicy.PUBLIC_ONLY,
    )
    ref = await provider.create_key(spec)
    jwk = await provider.get_public_jwk(ref.kid)
    print(jwk)


asyncio.run(main())
```

Keys can also be rotated, and the provider will track key versions:

```python
ref = await provider.create_key(spec)
await provider.rotate_key(ref.kid)
assert await provider.list_versions(ref.kid) == (1, 2)
```

Existing keys can be imported from PEM or OpenSSH data and exposed via JWKS:

```python
from pathlib import Path

pem = Path("id_ed25519").read_bytes()
ref = await provider.import_key(spec, pem)
jwks = await provider.jwks()
```
