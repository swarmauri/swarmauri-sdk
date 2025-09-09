<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


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
