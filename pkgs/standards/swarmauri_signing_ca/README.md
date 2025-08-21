![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

# Swarmauri Signing CA

A CA-capable detached signer implementing the `ISigning` interface with X.509 utilities for creating and validating certificate chains.

Features:
- JSON canonicalization (built-in)
- Optional CBOR canonicalization via `cbor2`
- Optional YAML canonicalization via `pyyaml`
- Detached signatures using `cryptography`
- Supports Ed25519, ECDSA (P-256) and RSA-PSS
- X.509 helpers for self-signed certificates, CSRs, and chain verification

## Installation

```bash
pip install swarmauri_signing_ca
```

## Usage

```python
from swarmauri_signing_ca import CASigner

signer = CASigner()
# create a KeyRef or object with `tags={"crypto_obj": private_key}`
```

## Entry Point

The signer registers under the `swarmauri.signings` entry point as `CASigner`.
