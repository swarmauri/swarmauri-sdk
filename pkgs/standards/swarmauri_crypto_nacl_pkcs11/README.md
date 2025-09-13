<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

<p align="center">
    <a href="https://pypi.org/project/swarmauri_crypto_nacl_pkcs11/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_crypto_nacl_pkcs11" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_crypto_nacl_pkcs11.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_nacl_pkcs11/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_crypto_nacl_pkcs11" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_nacl_pkcs11/">
        <img src="https://img.shields.io/pypi/l/swarmauri_crypto_nacl_pkcs11" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_nacl_pkcs11/">
        <img src="https://img.shields.io/pypi/v/swarmauri_crypto_nacl_pkcs11?label=swarmauri_crypto_nacl_pkcs11&color=green" alt="PyPI - swarmauri_crypto_nacl_pkcs11"/></a>
</p>

---

## Swarmauri Crypto NaCl PKCS#11

Hybrid crypto provider using PyNaCl for Ed25519/X25519 operations and `python-pkcs11` for AES-KW key wrapping. Implements the `ICrypto` contract via `CryptoBase`.

- AES-GCM symmetric encrypt/decrypt
- AES-KW wrap/unwrap using PKCS#11
- X25519 sealed boxes for single and multi-recipient encryption

## Installation

```bash
pip install swarmauri_crypto_nacl_pkcs11
```

## Usage

```python
from swarmauri_crypto_nacl_pkcs11 import NaClPkcs11Crypto
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy

crypto = NaClPkcs11Crypto()

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

The provider is registered under the `swarmauri.cryptos` entry-point as `NaClPkcs11Crypto`.
