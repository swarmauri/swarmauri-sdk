![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_keyprovider_file/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_keyprovider_file" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_keyprovider_file/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_keyprovider_file.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_file/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_keyprovider_file" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_file/">
        <img src="https://img.shields.io/pypi/l/swarmauri_keyprovider_file" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_file/">
        <img src="https://img.shields.io/pypi/v/swarmauri_keyprovider_file?label=swarmauri_keyprovider_file&color=green" alt="PyPI - swarmauri_keyprovider_file"/></a>
</p>

---

# Swarmauri File Key Provider

`FileKeyProvider` is a file-backed implementation of the `KeyProviderBase`
interface. It persists each key beneath a `keys/<kid>/v<version>/` directory,
captures metadata in `meta.json`, and exports public material in PEM or JWK
form. The provider supports the same lifecycle semantics as the in-memory
providers, but every operation is durable on disk.

## Highlights

- Generate symmetric AES-256-GCM keys and asymmetric Ed25519, X25519, RSA
  (OAEP/PSS), or ECDSA (P-256) key material.
- Import existing keys while preserving private material when allowed by the
  selected `ExportPolicy`.
- Rotate versions in-place, destroy versions or entire keys, and list
  historical versions stored on disk.
- Publish public material as individual JWKs or aggregate JWKS documents and
  expose HKDF and random byte helpers.

## Installation

Choose the tool that matches your workflow:

```bash
# pip
pip install swarmauri_keyprovider_file

# Poetry
poetry add swarmauri_keyprovider_file

# uv
uv add swarmauri_keyprovider_file
```

## Usage

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

`FileKeyProvider` is asynchronous—every lifecycle method returns a
`KeyRef`. Use `include_secret=True` when retrieving keys that allow private
material export so symmetric key bytes are loaded from disk.

## Entry Point

The provider registers under the `swarmauri.key_providers` entry point as `FileKeyProvider`.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.