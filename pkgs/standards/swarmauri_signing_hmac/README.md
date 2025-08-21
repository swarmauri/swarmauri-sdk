![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

# Swarmauri Signing HMAC

An HMAC-based signer implementing the `ISigning` interface for detached
signatures over raw bytes and canonicalized envelopes.

Features:
- JSON canonicalization (always available)
- Optional CBOR canonicalization via `cbor2`
- Detached signatures using standard library `hmac`

## Installation

```bash
pip install swarmauri_signing_hmac
```

## Usage

```python
from swarmauri_signing_hmac import HmacEnvelopeSigner

signer = HmacEnvelopeSigner()
# create a KeyRef for a secret; see swarmauri_core for details
```

## Entry Point

The signer registers under the `swarmauri.signings` entry point as `HmacEnvelopeSigner`.
