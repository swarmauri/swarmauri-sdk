![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_signing_rsa/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_signing_rsa" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_rsa/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_rsa.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_rsa/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_signing_rsa" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_rsa/">
        <img src="https://img.shields.io/pypi/l/swarmauri_signing_rsa" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_rsa/">
        <img src="https://img.shields.io/pypi/v/swarmauri_signing_rsa?label=swarmauri_signing_rsa&color=green" alt="PyPI - swarmauri_signing_rsa"/></a>
</p>

---

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
