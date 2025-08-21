![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_signing_pgp/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_signing_pgp" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_pgp/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_pgp.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_pgp/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_signing_pgp" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_pgp/">
        <img src="https://img.shields.io/pypi/l/swarmauri_signing_pgp" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_pgp/">
        <img src="https://img.shields.io/pypi/v/swarmauri_signing_pgp?label=swarmauri_signing_pgp&color=green" alt="PyPI - swarmauri_signing_pgp"/></a>
</p>

---

# Swarmauri Signing PGP

OpenPGP envelope signer for Swarmauri. Supports JSON and optional CBOR canonicalization.

## Installation

```bash
pip install swarmauri_signing_pgp
```

To enable CBOR canonicalization:

```bash
pip install swarmauri_signing_pgp[cbor]
```

## Usage

```python
from swarmauri_signing_pgp import PgpEnvelopeSigner

signer = PgpEnvelopeSigner()
# ... use signer.sign_bytes or signer.sign_envelope
```
