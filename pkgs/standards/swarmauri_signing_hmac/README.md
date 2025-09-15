![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_signing_hmac/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_signing_hmac" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_hmac/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_hmac.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_hmac/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_signing_hmac" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_hmac/">
        <img src="https://img.shields.io/pypi/l/swarmauri_signing_hmac" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_hmac/">
        <img src="https://img.shields.io/pypi/v/swarmauri_signing_hmac?label=swarmauri_signing_hmac&color=green" alt="PyPI - swarmauri_signing_hmac"/></a>
</p>

---

# Swarmauri Signing HMAC

An HMAC-based signer implementing the `ISigning` interface for detached
signatures over raw bytes and canonicalized envelopes.

## Features

- JSON canonicalization (always available)
- Optional CBOR canonicalization via `cbor2`
- Detached signatures using standard library `hmac`

## Security Notes

- Supports HMAC-SHA-256/384/512 only.
- Keys must be at least 32 bytes (256 bits).
- Tags default to the hash digest size and may be truncated via
  `opts["tag_size"]` but not below 16 bytes (128 bits).

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

    # KeyRef with a raw 32-byte secret; see swarmauri_core for more options
    key = {"kind": "raw", "key": "a" * 32}

    # Sign and verify raw bytes
    payload = b"hello"
    sigs = await signer.sign_bytes(key, payload, alg=JWAAlg.HS256, opts={"tag_size": 16})
    assert await signer.verify_bytes(payload, sigs, opts={"keys": [key]})

    # Sign and verify a JSON envelope
    env = {"msg": "hello"}
    sigs_env = await signer.sign_envelope(
        key, env, alg=JWAAlg.HS256, canon="json", opts={"tag_size": 16}
    )
    assert await signer.verify_envelope(env, sigs_env, canon="json", opts={"keys": [key]})


asyncio.run(main())
```

Verification requires providing one or more keys via `opts["keys"]`.

## Entry Point

The signer registers under the `swarmauri.signings` entry point as `HmacEnvelopeSigner`.
