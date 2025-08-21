# swarmauri_mre_crypto_pgpseal

OpenPGP sealed-per-recipient Multi-Recipient Encryption (MRE) provider for the Swarmauri framework.

## Features

- Implements `IMreCrypto` with sealed-per-recipient mode only.
- Each recipient receives a PGP-encrypted copy of the plaintext.
- Optional CBOR canonicalization via the `cbor` extra.

## Installation

```bash
pip install swarmauri_mre_crypto_pgpseal
```

To enable optional CBOR support:

```bash
pip install swarmauri_mre_crypto_pgpseal[cbor]
```

## Usage

```python
from swarmauri_mre_crypto_pgpseal import PGPSealMreCrypto

crypto = PGPSealMreCrypto()
# ... load KeyRefs and encrypt
```
