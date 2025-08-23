![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

# Swarmauri SSH Key Provider

Interfaces with local SSH keys to generate and manage signing keys.

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
