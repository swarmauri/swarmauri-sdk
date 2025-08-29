![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

# Swarmauri Signing RSA

An RSA-based signer implementing the `ISigning` interface for detached
signatures over raw bytes and canonicalized envelopes.

Features:
- JSON canonicalization (always available)
- Optional CBOR canonicalization via `cbor2`
- Detached signatures using `cryptography`'s RSA primitives
- Supports `RSA-PSS-SHA256` (recommended) and `RS256`

## Installation

```bash
pip install swarmauri_signing_rsa
```

## Usage

```python
from swarmauri_signing_rsa import RSAEnvelopeSigner

signer = RSAEnvelopeSigner()
# create a KeyRef for an RSA private key; see swarmauri_core for details
```

## Entry Point

The signer registers under the `swarmauri.signings` entry point as `RSAEnvelopeSigner`.
