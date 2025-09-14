![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_crypto_sodium/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_crypto_sodium" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_crypto_sodium/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_crypto_sodium.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_sodium/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_crypto_sodium" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_sodium/">
        <img src="https://img.shields.io/pypi/l/swarmauri_crypto_sodium" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_sodium/">
        <img src="https://img.shields.io/pypi/v/swarmauri_crypto_sodium?label=swarmauri_crypto_sodium&color=green" alt="PyPI - swarmauri_crypto_sodium"/></a>
</p>

---

## Swarmauri Crypto Sodium

Libsodium-backed crypto provider implementing the `ICrypto` contract via `CryptoBase`.

- XChaCha20-Poly1305 symmetric encrypt/decrypt
- X25519 sealed boxes for data sealing and key wrapping
- Multi-recipient envelopes using XChaCha20-Poly1305 + X25519 sealed wrap

## Installation

```bash
pip install swarmauri_crypto_sodium
```

## Usage

```python
from swarmauri_crypto_sodium import SodiumCrypto
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy

crypto = SodiumCrypto()

sym = KeyRef(
    kid="sym1",
    version=1,
    type=KeyType.SYMMETRIC,
    uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
    export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    material=b"\x00" * 32,
)

ct = await crypto.encrypt(sym, b"hello")
pt = await crypto.decrypt(sym, ct)
```

## Entry point

The provider is registered under the `swarmauri.cryptos` entry-point as `SodiumCrypto`.
