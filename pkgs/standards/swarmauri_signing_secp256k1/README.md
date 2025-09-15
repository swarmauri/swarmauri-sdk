![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_signing_secp256k1/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_signing_secp256k1" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_secp256k1/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_secp256k1.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_secp256k1/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_signing_secp256k1" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_secp256k1/">
        <img src="https://img.shields.io/pypi/l/swarmauri_signing_secp256k1" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_secp256k1/">
        <img src="https://img.shields.io/pypi/v/swarmauri_signing_secp256k1?label=swarmauri_signing_secp256k1&color=green" alt="PyPI - swarmauri_signing_secp256k1"/></a>
</p>

---

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
