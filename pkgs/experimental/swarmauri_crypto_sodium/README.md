![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_crypto_sodium/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_crypto_sodium" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_crypto_sodium/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_crypto_sodium.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_crypto_sodium/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_crypto_sodium" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_crypto_sodium/">
        <img src="https://img.shields.io/pypi/l/swarmauri_crypto_sodium" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_crypto_sodium/">
        <img src="https://img.shields.io/pypi/v/swarmauri_crypto_sodium?label=swarmauri_crypto_sodium&color=green" alt="PyPI - swarmauri_crypto_sodium"/>
    </a>
</p>

---

# Swarmauri Crypto Sodium

`Swarmauri Crypto Sodium` is a high-performance cryptography provider powered by [libsodium](https://github.com/jedisct1/libsodium). It implements the `ICrypto` contract via `CryptoBase`, enabling fast and secure cryptographic operations inside the Swarmauri ecosystem.

## Features

- **XChaCha20-Poly1305** symmetric encryption and decryption
- **X25519 sealed boxes** for data sealing and key wrapping
- **Multi-recipient envelopes** combining XChaCha20-Poly1305 and X25519

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

## Entry Point

The provider registers under the `swarmauri.cryptos` entry point as `SodiumCrypto`.

## License

This project is licensed under the terms of the [MIT License](LICENSE).

