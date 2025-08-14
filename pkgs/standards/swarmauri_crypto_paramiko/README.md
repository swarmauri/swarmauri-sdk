![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_crypto_paramiko/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_crypto_paramiko" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_crypto_paramiko/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_crypto_paramiko.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_paramiko/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_crypto_paramiko" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_paramiko/">
        <img src="https://img.shields.io/pypi/l/swarmauri_crypto_paramiko" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_paramiko/">
        <img src="https://img.shields.io/pypi/v/swarmauri_crypto_paramiko?label=swarmauri_crypto_paramiko&color=green" alt="PyPI - swarmauri_crypto_paramiko"/></a>
</p>

---

## Swarmauri Crypto Paramiko

Paramiko-backed crypto provider implementing the `ICrypto` contract via `CryptoBase`.

- AES-256-GCM symmetric encrypt/decrypt
- RSA-OAEP(SHA-256) wrap/unwrap
- Multi-recipient hybrid envelopes using OpenSSH public keys

## Installation

```bash
pip install swarmauri_crypto_paramiko
```

## Usage

```python
from swarmauri_crypto_paramiko import ParamikoCrypto
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy

crypto = ParamikoCrypto()

# Symmetric key for AEAD
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

The provider is registered under the `swarmauri.cryptos` entry-point as `ParamikoCrypto`.
