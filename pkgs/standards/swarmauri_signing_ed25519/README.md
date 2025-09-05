![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

# Swarmauri Signing Ed25519

An Ed25519-based signer implementing the `ISigning` interface for detached
signatures over raw bytes and canonicalized envelopes.

Features:
- JSON canonicalization (always available)
- Optional CBOR canonicalization via `cbor2`
- Detached signatures using `cryptography`'s Ed25519 primitives

## Installation

```bash
pip install swarmauri_signing_ed25519
```

## Usage

```python
from swarmauri_signing_ed25519 import Ed25519EnvelopeSigner

signer = Ed25519EnvelopeSigner()
# create a KeyRef for an Ed25519 private key; see swarmauri_core for details
```

## Entry Point

The signer registers under the `swarmauri.signings` entry point as `Ed25519EnvelopeSigner`.
