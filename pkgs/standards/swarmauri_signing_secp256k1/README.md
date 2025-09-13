<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

# Swarmauri Signing Secp256k1

A secp256k1 ECDSA signer implementing the `ISigning` interface for detached
signatures over raw bytes and canonicalized envelopes.

Features:
- JSON canonicalization (always available)
- Optional CBOR canonicalization via `cbor2`
- Detached signatures using `cryptography`'s secp256k1 primitives

## Installation

```bash
pip install swarmauri_signing_secp256k1
```

## Usage

```python
from swarmauri_signing_secp256k1 import Secp256k1EnvelopeSigner

signer = Secp256k1EnvelopeSigner()
# create a KeyRef for a secp256k1 private key; see swarmauri_core for details
```

## Entry Point

The signer registers under the `swarmauri.signings` entry point as `Secp256k1EnvelopeSigner`.
