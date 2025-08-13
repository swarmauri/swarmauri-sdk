# swarmauri_crypto_paramiko

Paramiko-backed crypto provider for Swarmauri that implements the `ICrypto` contract via `CryptoBase`.

Features:

- AES-256-GCM symmetric encrypt/decrypt
- RSA-OAEP(SHA-256) wrap/unwrap
- Multi-recipient envelopes using OpenSSH public keys

## Install

This package is part of the Swarmauri workspace. In a standalone environment:

```bash
pip install swarmauri_crypto_paramiko
```

## Usage

```python
from swarmauri_crypto_paramiko import ParamikoCrypto
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy

crypto = ParamikoCrypto()

# symmetric key for AEAD
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

The provider is exported under `swarmauri.cryptos` entry-point as `ParamikoCrypto`.
