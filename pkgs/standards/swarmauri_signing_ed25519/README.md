![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_signing_ed25519/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_signing_ed25519" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_ed25519/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_ed25519.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_ed25519/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_signing_ed25519" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_ed25519/">
        <img src="https://img.shields.io/pypi/l/swarmauri_signing_ed25519" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_ed25519/">
        <img src="https://img.shields.io/pypi/v/swarmauri_signing_ed25519?label=swarmauri_signing_ed25519&color=green" alt="PyPI - swarmauri_signing_ed25519"/></a>
</p>

---

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
