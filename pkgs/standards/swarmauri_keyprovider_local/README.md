![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

# Swarmauri Local Key Provider

Provides a simple in-memory key provider for development and testing.

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
