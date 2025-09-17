![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_keyprovider_ssh/"><img src="https://img.shields.io/pypi/dm/swarmauri_keyprovider_ssh" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_keyprovider_ssh/"><img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_keyprovider_ssh.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_ssh/"><img src="https://img.shields.io/pypi/pyversions/swarmauri_keyprovider_ssh" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_ssh/"><img src="https://img.shields.io/pypi/l/swarmauri_keyprovider_ssh" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_ssh/"><img src="https://img.shields.io/pypi/v/swarmauri_keyprovider_ssh?label=swarmauri_keyprovider_ssh&color=green" alt="PyPI - swarmauri_keyprovider_ssh"/></a>
</p>

# Swarmauri SSH Key Provider

An asynchronous `KeyProviderBase` implementation that keeps SSH key material in
memory and bridges it to Swarmauri's signing abstractions.

## Features

- Generate new Ed25519, RSA-PSS (SHA-256), or ECDSA P-256 key pairs on demand.
- Import existing private keys (PEM) or public keys (OpenSSH) while respecting
  each key's `ExportPolicy`.
- Rotate keys, enumerate versions, and optionally destroy specific versions or
  entire key identifiers.
- Export public keys as RFC 7517-compliant JWKs/JWKS with OpenSSH fingerprints
  embedded in the `tags` metadata.
- Produce random bytes and derive keying material using the HKDF construction
  (RFC 5869).

## Installation

Choose the tool that matches your workflow:

```bash
# pip
pip install swarmauri_keyprovider_ssh

# Poetry
poetry add swarmauri_keyprovider_ssh

# uv
uv add swarmauri_keyprovider_ssh
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

Use `destroy_key()` to remove an entire key identifier or just a single
version, and `jwks(prefix_kids=...)` when you need to emit a filtered JWKS for
downstream consumers.

Existing keys can be imported from PEM or OpenSSH data and exposed via JWKS:

```python
from pathlib import Path

pem = Path("id_ed25519").read_bytes()
ref = await provider.import_key(spec, pem)
jwks = await provider.jwks()
```
