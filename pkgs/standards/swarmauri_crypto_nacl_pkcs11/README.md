![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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

`swarmauri_crypto_nacl_pkcs11` is a hybrid crypto provider that combines [PyNaCl](https://pynacl.readthedocs.io) for X25519 sealed-box operations with [`python-pkcs11`](https://python-pkcs11.readthedocs.io) for AES key wrapping. The provider implements the `CryptoBase` contract and is discoverable via the `swarmauri.cryptos` entry-point as `NaClPkcs11Crypto`.

### Supported operations

- **AES-GCM authenticated encryption** via `encrypt`/`decrypt` using symmetric `KeyRef` material that is exactly 16, 24, or 32 bytes long.
- **AES Key Wrap (AES-KW)** via `wrap`/`unwrap` against an HSM-protected key. The PKCS#11 session is resolved from the `KeyRef.tags` (`module`, `slot_label`, `user_pin`, `label`) or the environment variables `PKCS11_MODULE`, `PKCS11_SLOT_LABEL`, `PKCS11_USER_PIN`, and `PKCS11_KEK_LABEL`.
- **X25519 sealed boxes** via `seal`/`unseal` and `encrypt_for_many`, enabling single or multi-recipient payload distribution. When additional authenticated data (AAD) is supplied the envelope is rebound with AES-GCM before delivery.

## Installation

Choose the workflow that matches your project:

```bash
pip install swarmauri_crypto_nacl_pkcs11
```

```bash
poetry add swarmauri_crypto_nacl_pkcs11
```

```bash
uv add swarmauri_crypto_nacl_pkcs11
```

## Usage

All cryptographic methods are asynchronous. The quick-start example below performs an AES-GCM round trip using a 256-bit symmetric key.

<!-- example-start -->
```python
import asyncio

from swarmauri_crypto_nacl_pkcs11 import NaClPkcs11Crypto
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse


async def main() -> None:
    crypto = NaClPkcs11Crypto()

    symmetric_key = KeyRef(
        kid="sym1",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=b"\x00" * 32,
    )

    ciphertext = await crypto.encrypt(symmetric_key, b"hello")
    plaintext = await crypto.decrypt(symmetric_key, ciphertext)
    assert plaintext == b"hello"


asyncio.run(main())
```
<!-- example-end -->

### Sealed box key exchange

`seal` and `encrypt_for_many` expect X25519 `KeyRef` instances. Provide the public key bytes via `KeyRef.public` for recipients and the private key bytes via `KeyRef.material` for unsealing. Each recipient receives an opaque sealed payload generated with `nacl.public.SealedBox`.

### PKCS#11-backed key wrapping

`wrap` and `unwrap` require a key-encryption-key (KEK) stored in the configured PKCS#11 slot. Supply connection details through `KeyRef.tags` or environment variables as described above. The wrapped material is returned as a `WrappedKey` using the `AES-KW` algorithm.
