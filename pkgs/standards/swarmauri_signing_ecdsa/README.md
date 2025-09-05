![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

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
