<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


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
