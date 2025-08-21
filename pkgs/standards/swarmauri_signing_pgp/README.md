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

## Swarmauri Signing PGP

OpenPGP detached signature provider implementing the `ISigning` contract.

- Canonicalization: JSON (built-in), optional CBOR via `cbor2`
- Detached OpenPGP signatures using the `PGPy` library

### Installation

```bash
pip install swarmauri_signing_pgp
```

### Usage

```python
from swarmauri_signing_pgp import PgpEnvelopeSigner
from swarmauri_core.crypto.types import KeyRef

signer = PgpEnvelopeSigner()

# Load or generate a pgpy key
import pgpy
key = pgpy.PGPKey.new(pgpy.constants.PubKeyAlgorithm.RSAEncryptOrSign, 2048)
uid = pgpy.PGPUID.new("Test", email="test@example.com")
key.add_uid(uid, usage={pgpy.constants.KeyFlags.Sign})

kref = {"kind": "pgpy_key", "priv": key}
sig = await signer.sign_bytes(kref, b"hello")
assert await signer.verify_bytes(b"hello", sig, opts={"pubkeys": [key]})
```

## Entry point

The provider is registered under the `swarmauri.signings` entry-point as `PgpEnvelopeSigner`.

