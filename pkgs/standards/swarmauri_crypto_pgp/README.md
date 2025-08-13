![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_crypto_pgp/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_crypto_pgp" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_crypto_pgp/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_crypto_pgp.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_pgp/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_crypto_pgp" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_pgp/">
        <img src="https://img.shields.io/pypi/l/swarmauri_crypto_pgp" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_pgp/">
        <img src="https://img.shields.io/pypi/v/swarmauri_crypto_pgp?label=swarmauri_crypto_pgp&color=green" alt="PyPI - swarmauri_crypto_pgp"/></a>
</p>

---

## Swarmauri Crypto PGP

OpenPGP (GnuPG-backed) crypto provider implementing the `ICrypto` contract.

- Symmetric AEAD: AES-256-GCM
- Key wrapping: OpenPGP public-key encryption (RSA keys recommended)
- Hybrid encrypt-for-many supported

### Key material expectations

- `encrypt`/`decrypt`: `KeyRef.material` must be 16/24/32 bytes for AES-GCM
- `wrap`/`encrypt_for_many`: `KeyRef.public` must be ASCII-armored OpenPGP public key bytes
- `unwrap`: `KeyRef.material` must be ASCII-armored OpenPGP private key bytes

## Installation

```bash
pip install swarmauri_crypto_pgp
```

## Usage

```python
from swarmauri_crypto_pgp import PGPCrypto
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy

crypto = PGPCrypto()

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

The provider is registered under the `swarmauri.cryptos` entry-point as `PGPCrypto`.
