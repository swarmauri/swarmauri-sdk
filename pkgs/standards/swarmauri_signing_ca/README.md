![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

# Swarmauri Signing CA

A certificate-authority-capable signer implementing the `ISigning` interface for detached
signatures over raw bytes and canonicalized envelopes. Provides helpers for creating CSRs,
signing certificates, and verifying simple chains.

Features:
- JSON canonicalization (built-in)
- Optional CBOR canonicalization via `cbor2`
- Supports Ed25519, ECDSA (P-256 and others), and RSA-PSS

## Installation

```bash
pip install swarmauri_signing_ca
```

## Usage

```python
from swarmauri_signing_ca import CASigner

signer = CASigner()
# create a KeyRef for a private key; see swarmauri_core for details
```

## Entry Point

The signer registers under the `swarmauri.signings` entry point as `CASigner`.
