![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# Swarmauri Signing ECDSA

An ECDSA-based signer implementing the `ISigning` interface for detached
signatures over raw bytes and canonicalized envelopes.

Features:
- JSON canonicalization (always available)
- Optional CBOR canonicalization via `cbor2`
- Supports curves P-256, P-384, P-521 with `cryptography`

## Installation

```bash
pip install swarmauri_signing_ecdsa
```

## Usage

```python
from swarmauri_signing_ecdsa import EcdsaEnvelopeSigner

signer = EcdsaEnvelopeSigner()
# create a KeyRef for an EC private key; see swarmauri_core for details
```

## Entry Point

The signer registers under the `swarmauri.signings` entry point as `EcdsaEnvelopeSigner`.
