<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


# Swarmauri File Key Provider

A file-backed key provider implementing the `KeyProviderBase` interface.
It manages symmetric and asymmetric keys on disk and exports public material via JWK/JWKS.

## Installation

```bash
pip install swarmauri_keyprovider_file
```

## Usage

```python
import asyncio
from tempfile import TemporaryDirectory

from swarmauri_keyprovider_file import FileKeyProvider
from swarmauri_core.keys.types import (
    ExportPolicy,
    KeyAlg,
    KeyClass,
    KeySpec,
)
from swarmauri_core.crypto.types import KeyUse


async def run_example() -> str:
    with TemporaryDirectory() as tmp:
        provider = FileKeyProvider(tmp)
        spec = KeySpec(
            klass=KeyClass.symmetric,
            alg=KeyAlg.AES256_GCM,
            uses=(KeyUse.ENCRYPT,),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        )
        created = await provider.create_key(spec)
        provider2 = FileKeyProvider(tmp)
        loaded = await provider2.get_key(created.kid, include_secret=True)
        print(f"Loaded key: {loaded.kid}")


asyncio.run(run_example())
```

## Entry Point

The provider registers under the `swarmauri.key_providers` entry point as `FileKeyProvider`.
