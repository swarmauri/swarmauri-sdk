![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_keyprovider_pkcs11/">
        <img src="https://static.pepy.tech/badge/swarmauri_keyprovider_pkcs11/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_keyprovider_pkcs11/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_keyprovider_pkcs11.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_pkcs11/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_pkcs11/">
        <img src="https://img.shields.io/pypi/l/swarmauri_keyprovider_pkcs11" alt="License"/></a>
    <a href="https://pypi.org/project/swarmauri_keyprovider_pkcs11/">
        <img src="https://img.shields.io/pypi/v/swarmauri_keyprovider_pkcs11?label=swarmauri_keyprovider_pkcs11&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Swarmauri Keyprovider PKCS#11

PKCS#11 hardware-backed key provider for Swarmauri.

## Features

- PKCS#11 hardware-backed key provider for Swarmauri.
- Exposes discoverable runtime entry points for `peagen.plugins.key_providers, swarmauri.key_providers` so the package can be wired into Swarmauri or Tigrbl workflows.
- Provides an experimental workspace surface for early validation before functionality graduates into a more stable package lane.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add swarmauri_keyprovider_pkcs11
```

```bash
pip install swarmauri_keyprovider_pkcs11
```

## Usage

Start by importing the public package surface, then configure the exported type or callable inside the workflow that consumes it.

```python
from swarmauri_keyprovider_pkcs11 import Pkcs11KeyProvider

exports = ['Pkcs11KeyProvider']
print(exports)
```

After import, pass the exported objects into the surrounding Swarmauri or Tigrbl code that owns configuration, credentials, transport, or storage details.

License: Apache-2.0. See `LICENSE`.
