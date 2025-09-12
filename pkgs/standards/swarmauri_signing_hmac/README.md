![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri-signing-hmac/">
        <img src="https://img.shields.io/pypi/dm/swarmauri-signing-hmac" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_hmac/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_hmac.svg"/></a>
    <a href="https://pypi.org/project/swarmauri-signing-hmac/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri-signing-hmac" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri-signing-hmac/">
        <img src="https://img.shields.io/pypi/l/swarmauri-signing-hmac" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri-signing-hmac/">
        <img src="https://img.shields.io/pypi/v/swarmauri-signing-hmac?label=swarmauri-signing-hmac&color=green" alt="PyPI - swarmauri-signing-hmac"/></a>
</p>

# Swarmauri Signing HMAC

An HMAC-based signer implementing the `ISigning` interface for detached
signatures over raw bytes and canonicalized envelopes.

Features:
- JSON canonicalization (always available)
- Optional CBOR canonicalization via `cbor2`
- Detached signatures using standard library `hmac`

## Installation

```bash
pip install swarmauri_signing_hmac
```

## Usage

```python
import asyncio
from swarmauri_signing_hmac import HmacEnvelopeSigner
from swarmauri_core.crypto.types import JWAAlg


async def main() -> None:
    signer = HmacEnvelopeSigner()

    # KeyRef with a raw secret; see swarmauri_core for more options
    key = {"kind": "raw", "key": "secret"}

    # Sign and verify raw bytes
    payload = b"hello"
    sigs = await signer.sign_bytes(key, payload, alg=JWAAlg.HS256)
    assert await signer.verify_bytes(payload, sigs, opts={"keys": [key]})

    # Sign and verify a JSON envelope
    env = {"msg": "hello"}
    sigs_env = await signer.sign_envelope(key, env, alg=JWAAlg.HS256, canon="json")
    assert await signer.verify_envelope(env, sigs_env, canon="json", opts={"keys": [key]})


asyncio.run(main())
```

Verification requires providing one or more keys via `opts["keys"]`.

## Entry Point

The signer registers under the `swarmauri.signings` entry point as `HmacEnvelopeSigner`.
