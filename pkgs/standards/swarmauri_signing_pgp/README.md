<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

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

The `swarmauri_signing_pgp` package provides an OpenPGP envelope signer for the
Swarmauri SDK. It can create and verify detached signatures over raw byte
payloads or canonicalized envelopes using JSON or optionally CBOR.

## Features

- Detached OpenPGP signatures for bytes and envelopes
- JSON canonicalization with optional CBOR support
- Verification of multiple signatures with a minimum signer threshold

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
from pgpy import PGPKey
from swarmauri_signing_pgp import PgpEnvelopeSigner

priv_key, _ = PGPKey.from_file("path/to/private.asc")
pub_key, _ = PGPKey.from_file("path/to/public.asc")

signer = PgpEnvelopeSigner()
sig = await signer.sign_bytes({"kind": "pgpy_key", "priv": priv_key}, b"data")

await signer.verify_bytes(
    b"data",
    sig,
    opts={"pubkeys": [pub_key]},
)
```

Replace the key-loading logic with your own. The signer can also operate on
envelopes by calling `sign_envelope` and `verify_envelope` after choosing a
canonicalization format.
