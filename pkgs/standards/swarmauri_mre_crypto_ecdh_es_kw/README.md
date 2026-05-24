![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_mre_crypto_ecdh_es_kw/">
        <img src="https://static.pepy.tech/badge/swarmauri_mre_crypto_ecdh_es_kw/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_mre_crypto_ecdh_es_kw/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_mre_crypto_ecdh_es_kw.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_mre_crypto_ecdh_es_kw/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/swarmauri_mre_crypto_ecdh_es_kw/">
        <img src="https://img.shields.io/pypi/l/swarmauri_mre_crypto_ecdh_es_kw" alt="License"/></a>
    <a href="https://pypi.org/project/swarmauri_mre_crypto_ecdh_es_kw/">
        <img src="https://img.shields.io/pypi/v/swarmauri_mre_crypto_ecdh_es_kw?label=swarmauri_mre_crypto_ecdh_es_kw&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Swarmauri Mre Crypto ECDH Es Kw

ECDH-ES+A128KW based multi-recipient encryption provider for Swarmauri.

## Features

- ECDH-ES+A128KW based multi-recipient encryption provider for Swarmauri.
- Exposes discoverable runtime entry points for `peagen.plugins.mre_cryptos, swarmauri.mre_cryptos` so the package can be wired into Swarmauri or Tigrbl workflows.
- Fits the standards package lane so the capability can be added to a project as a focused, separately versioned dependency.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add swarmauri_mre_crypto_ecdh_es_kw
```

```bash
pip install swarmauri_mre_crypto_ecdh_es_kw
```

## Usage

Start by importing the public package surface, then configure the exported type or callable inside the workflow that consumes it.

```python
from swarmauri_mre_crypto_ecdh_es_kw import EcdhEsA128KwMreCrypto

exports = ['EcdhEsA128KwMreCrypto']
print(exports)
```

After import, pass the exported objects into the surrounding Swarmauri or Tigrbl code that owns configuration, credentials, transport, or storage details.

License: Apache-2.0. See `LICENSE`.
