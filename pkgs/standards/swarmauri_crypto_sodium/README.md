
![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_distance_minkowski/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_distance_minkowski" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_distance_minkowski/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_distance_minkowski.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_distance_minkowski/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_distance_minkowski" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_distance_minkowski/">
        <img src="https://img.shields.io/pypi/l/swarmauri_distance_minkowski" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_distance_minkowski/">
        <img src="https://img.shields.io/pypi/v/swarmauri_distance_minkowski?label=swarmauri_distance_minkowski&color=green" alt="PyPI - swarmauri_distance_minkowski"/></a>
</p>

---

# Swarmauri Crypto Sodium

Libsodium-backed crypto provider implementing the `ICrypto` contract via `CryptoBase`.

## Features

- XChaCha20-Poly1305 symmetric encrypt/decrypt
- X25519 sealed boxes for data sealing and key wrapping
- Multi-recipient envelopes using XChaCha20-Poly1305 + X25519 sealed wrap
- **Bundled libsodium**: No need to install libsodium separately!

## Installation

```bash
pip install swarmauri_crypto_sodium
```

## Usage

```python
from swarmauri_crypto_sodium import SodiumCrypto
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy
import asyncio

async def example():
    crypto = SodiumCrypto()

    # Create a symmetric key
    sym = KeyRef(
        kid="sym1",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=b"\x00" * 32,
    )

    # Encrypt and decrypt
    ct = await crypto.encrypt(sym, b"hello world")
    pt = await crypto.decrypt(sym, ct)
    print(f"Decrypted: {pt.decode()}")

asyncio.run(example())
```

## Build System

This package uses Meson build system to bundle libsodium directly with the Python package, eliminating the need for users to install libsodium system-wide.

## Entry Point

The provider is registered under the `swarmauri.cryptos` entry-point as `SodiumCrypto`.
