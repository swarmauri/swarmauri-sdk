![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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

The `swarmauri_signing_pgp` package provides an OpenPGP signer for the Swarmauri
SDK. It creates and verifies detached signatures over raw byte payloads or
structured envelopes that are canonicalized to JSON or, optionally, CBOR.

## Features

- Detached OpenPGP signatures for bytes and envelopes
- JSON canonicalization with optional CBOR support via `cbor2`
- Multi-signer verification with configurable minimum signer requirements
- Private key loading from in-memory `pgpy` objects or ASCII-armored blobs
- Passphrase handling for locked private keys

## Installation

Install the package with your preferred Python packaging tool:

```bash
pip install swarmauri_signing_pgp
```

```bash
poetry add swarmauri_signing_pgp
```

```bash
uv pip install swarmauri_signing_pgp
```

### Optional CBOR support

Enable canonicalization to CBOR by installing the optional dependency group:

```bash
pip install "swarmauri_signing_pgp[cbor]"
```

```bash
poetry add swarmauri_signing_pgp -E cbor
```

```bash
uv pip install "swarmauri_signing_pgp[cbor]"
```

## Usage

The signer exposes asynchronous methods from the Swarmauri signing base class.
Key references are dictionaries describing how to load private keys. For `pgpy`
objects, the signer expects a mapping such as `{"kind": "pgpy_key", "priv":
pgpy_key}`. Verification requires the corresponding public keys supplied in the
`opts={"pubkeys": [...]}` argument.

### Sign and verify raw bytes

```python
import asyncio

from pgpy import PGPKey, PGPUID
from pgpy.constants import (
    CompressionAlgorithm,
    HashAlgorithm,
    KeyFlags,
    PubKeyAlgorithm,
    SymmetricKeyAlgorithm,
)

from swarmauri_signing_pgp import PgpEnvelopeSigner


def make_demo_key() -> PGPKey:
    key = PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 2048)
    uid = PGPUID.new("Example User", email="user@example.com")
    key.add_uid(
        uid,
        usage={KeyFlags.Sign},
        hashes=[HashAlgorithm.SHA256],
        ciphers=[SymmetricKeyAlgorithm.AES256],
        compression=[CompressionAlgorithm.ZLIB],
    )
    return key


async def main() -> None:
    signer = PgpEnvelopeSigner()
    key = make_demo_key()
    key_ref = {"kind": "pgpy_key", "priv": key}
    payload = b"openpgp demo"

    signatures = await signer.sign_bytes(key_ref, payload)
    verified = await signer.verify_bytes(
        payload,
        signatures,
        opts={"pubkeys": [key.pubkey]},
    )
    print("Verified:", verified)


asyncio.run(main())
```

The signer returns detached signatures that include both binary and ASCII-armored
representations. Passphrases for locked private keys can be supplied through
`opts={"passphrase": "secret"}`.

### Sign envelopes

Envelopes are canonicalized before signing. JSON canonicalization is always
available and CBOR becomes available when the optional dependency group is
installed:

```python
envelope = {"subject": "demo", "body": "hello"}
signatures = await signer.sign_envelope(key_ref, envelope, canon="json")
await signer.verify_envelope(
    envelope,
    signatures,
    canon="json",
    opts={"pubkeys": [key.pubkey]},
)
```

Use `canon="cbor"` to opt into CBOR canonicalization. The `supports()` helper
exposes the available algorithms, canonicalization formats, and feature flags at
runtime.
