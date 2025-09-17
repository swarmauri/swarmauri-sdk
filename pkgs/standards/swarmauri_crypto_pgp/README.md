![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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

`PGPCrypto` is an OpenPGP (GnuPG-backed) crypto provider that implements the
`ICrypto` contract from `swarmauri_core`. It combines modern AEAD primitives
with OpenPGP public-key operations so that the same component can handle
symmetrical encryption, public-key key wrapping, and hybrid envelopes.

### Features at a glance

- **Symmetric AEAD** – AES-256-GCM powers `encrypt` and `decrypt`.
- **Key wrapping** – `wrap` and `unwrap` delegate to GnuPG to protect random or
  supplied key material with a recipient's public/private key pair.
- **Hybrid envelopes** – `encrypt_for_many` supports both traditional
  KEM+AEAD (shared ciphertext + wrapped session key) and OpenPGP sealed mode for
  per-recipient ciphertexts.
- **Sealing convenience** – `seal` and `unseal` provide single-recipient
  OpenPGP public-key encryption without managing the envelope structure.

### System requirements

- Python 3.10 – 3.13.
- [GnuPG](https://gnupg.org/) available on the `PATH` (required by
  `python-gnupg`).

### Key material expectations

- `encrypt` / `decrypt`: `KeyRef.material` must be 16/24/32 bytes for AES-GCM.
- `wrap` / `encrypt_for_many`: `KeyRef.public` must be ASCII-armored OpenPGP
  public key bytes.
- `unwrap` / `unseal`: `KeyRef.material` must be ASCII-armored OpenPGP private
  key bytes. Supply a passphrase via `KeyRef.tags["passphrase"]` when needed.

## Installation

Choose the tool that matches your workflow:

```bash
# pip
pip install swarmauri_crypto_pgp

# Poetry
poetry add swarmauri_crypto_pgp

# uv
uv add swarmauri_crypto_pgp
```

## Quickstart

The snippet below mirrors the asynchronous usage exercised in the tests. It
creates a symmetric `KeyRef`, encrypts plaintext, and decrypts the resulting
`AEADCiphertext` back to bytes.

```python
import asyncio

from swarmauri_crypto_pgp import PGPCrypto
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse


async def main() -> None:
    crypto = PGPCrypto()

    # Symmetric key for AES-256-GCM
    sym = KeyRef(
        kid="sym1",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=b"\x00" * 32,
    )

    ct = await crypto.encrypt(sym, b"hello OpenPGP")
    pt = await crypto.decrypt(sym, ct)

    print(pt)


if __name__ == "__main__":
    asyncio.run(main())
```

### Working with recipients

- Call `encrypt_for_many` with recipient public keys to either produce an
  AES-GCM ciphertext with OpenPGP-wrapped session keys (default) or
  per-recipient sealed blobs by passing `enc_alg="OpenPGP-SEAL"`.
- Use `seal` / `unseal` for single-recipient OpenPGP public-key encryption.
- `wrap` and `unwrap` offer direct access to OpenPGP-based key encapsulation.

## Entry point

The provider is registered under the `swarmauri.cryptos` entry-point as
`PGPCrypto`.
