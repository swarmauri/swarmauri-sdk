![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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
