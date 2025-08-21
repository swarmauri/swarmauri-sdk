![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

# Swarmauri Signing CASigner

A certificate-authority capable signer implementing the `ISigning` interface for detached signatures and X.509 utilities.

Features:
- JSON canonicalization (always available)
- Optional CBOR canonicalization via `cbor2`
- Detached signatures for Ed25519, ECDSA, and RSA keys
- Utilities for issuing and verifying X.509 certificate chains

## Installation

```bash
pip install swarmauri_signing_casigner
```

## Usage

```python
from swarmauri_signing_casigner import CASigner

signer = CASigner()
# create a KeyRef for a supported private key; see swarmauri_core for details
```

## Entry Point

The signer registers under the `swarmauri.signings` entry point as `CASigner`.
