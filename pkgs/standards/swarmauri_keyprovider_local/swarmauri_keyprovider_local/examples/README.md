![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_keyprovider_local/">
        <img src="https://static.pepy.tech/badge/swarmauri_keyprovider_local/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_keyprovider_local/swarmauri_keyprovider_local/examples/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_keyprovider_local/swarmauri_keyprovider_local/examples.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_local/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_local/">
        <img src="https://img.shields.io/pypi/l/swarmauri_keyprovider_local" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_local/">
        <img src="https://img.shields.io/pypi/v/swarmauri_keyprovider_local?label=swarmauri_keyprovider_local&color=green" alt="PyPI - swarmauri_keyprovider_local"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# LocalKeyProvider Examples

This example demonstrates creating and retrieving a symmetric key with `LocalKeyProvider`.

```python
import asyncio
from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_core.key_providers.types import (
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


