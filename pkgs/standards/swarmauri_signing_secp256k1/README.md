<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
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
