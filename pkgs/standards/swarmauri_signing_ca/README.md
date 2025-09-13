![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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
