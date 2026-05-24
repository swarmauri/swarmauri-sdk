![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_mre_crypto_keyring/">
        <img src="https://static.pepy.tech/badge/swarmauri_mre_crypto_keyring/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_mre_crypto_keyring/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_mre_crypto_keyring.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_mre_crypto_keyring/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/swarmauri_mre_crypto_keyring/">
        <img src="https://img.shields.io/pypi/l/swarmauri_mre_crypto_keyring" alt="License"/></a>
    <a href="https://pypi.org/project/swarmauri_mre_crypto_keyring/">
        <img src="https://img.shields.io/pypi/v/swarmauri_mre_crypto_keyring?label=swarmauri_mre_crypto_keyring&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Swarmauri Mre Crypto Keyring

Keyring-backed multi-recipient encryption provider for Swarmauri.

## Features

- Keyring-backed multi-recipient encryption provider for Swarmauri.
- Exposes discoverable runtime entry points for `swarmauri.mre_cryptos` so the package can be wired into Swarmauri or Tigrbl workflows.
- Fits the standards package lane so the capability can be added to a project as a focused, separately versioned dependency.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add swarmauri_mre_crypto_keyring
```

```bash
pip install swarmauri_mre_crypto_keyring
```

## Usage

Start by importing the public package surface, then configure the exported type or callable inside the workflow that consumes it.

```python
from swarmauri_mre_crypto_keyring import KeyringMreCrypto

exports = ['KeyringMreCrypto']
print(exports)
```

After import, pass the exported objects into the surrounding Swarmauri or Tigrbl code that owns configuration, credentials, transport, or storage details.

License: Apache-2.0. See `LICENSE`.
