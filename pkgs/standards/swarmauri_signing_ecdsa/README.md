![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_signing_ecdsa/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_signing_ecdsa" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_ecdsa/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_ecdsa.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_ecdsa/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_signing_ecdsa" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_ecdsa/">
        <img src="https://img.shields.io/pypi/l/swarmauri_signing_ecdsa" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_ecdsa/">
        <img src="https://img.shields.io/pypi/v/swarmauri_signing_ecdsa?label=swarmauri_signing_ecdsa&color=green" alt="PyPI - swarmauri_signing_ecdsa"/></a>
</p>

---

# Swarmauri Signing ECDSA

An ECDSA-based signer implementing the `ISigning` interface for detached
signatures over raw bytes and canonicalized envelopes.

Features:
- JSON canonicalization (always available)
- Optional CBOR canonicalization via `cbor2`
- Supports curves P-256, P-384, P-521 with `cryptography`

## Installation

```bash
pip install swarmauri_signing_ecdsa
```

## Usage

```python
from swarmauri_signing_ecdsa import EcdsaEnvelopeSigner

signer = EcdsaEnvelopeSigner()
# create a KeyRef for an EC private key; see swarmauri_core for details
```

## Entry Point

The signer registers under the `swarmauri.signings` entry point as `EcdsaEnvelopeSigner`.
