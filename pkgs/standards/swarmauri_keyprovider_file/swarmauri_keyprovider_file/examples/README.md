![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_keyprovider_file/">
        <img src="https://static.pepy.tech/badge/swarmauri_keyprovider_file/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_keyprovider_file/swarmauri_keyprovider_file/examples/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_keyprovider_file/swarmauri_keyprovider_file/examples.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_file/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_file/">
        <img src="https://img.shields.io/pypi/l/swarmauri_keyprovider_file" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_file/">
        <img src="https://img.shields.io/pypi/v/swarmauri_keyprovider_file?label=swarmauri_keyprovider_file&color=green" alt="PyPI - swarmauri_keyprovider_file"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# FileKeyProvider Examples

This example shows how to persist a symmetric key using `FileKeyProvider`.

```python
import asyncio
from tempfile import TemporaryDirectory

from swarmauri_keyprovider_file import FileKeyProvider
from swarmauri_core.key_providers.types import (
    ExportPolicy,
    KeyAlg,
    KeyClass,
    KeySpec,
)
from swarmauri_core.crypto.types import KeyUse


async def run_example() -> str:
    """Persist a symmetric key on disk using FileKeyProvider."""
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
        assert loaded.material == created.material
        return loaded.kid


if __name__ == "__main__":
    print(asyncio.run(run_example()))
```


