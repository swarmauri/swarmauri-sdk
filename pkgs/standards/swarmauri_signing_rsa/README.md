![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


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

An asynchronous RSA signer implementing the `ISigning` interface for detached
signatures over raw bytes and canonicalized envelopes.

## Capabilities

- Detached signatures for byte payloads as well as canonicalized envelopes
- JSON canonicalization is built in; CBOR canonicalization is available when
  [`cbor2`](https://pypi.org/project/cbor2/) is installed
- RSA-PSS-SHA256 (default) and RS256 signature algorithms powered by
  [`cryptography`](https://pypi.org/project/cryptography/)
- Verification requires the expected RSA public keys to be provided through
  `opts["pubkeys"]`, enabling multi-signer verification scenarios
- Private and public keys can be supplied as PEM strings, filesystem paths,
  RFC 7517 JWKs, or raw `cryptography` key objects via Swarmauri `KeyRef`
  dictionaries

## Installation

Pick the tool that matches your workflow:

```bash
# pip
pip install swarmauri_signing_rsa

# Poetry
poetry add swarmauri_signing_rsa

# uv
uv add swarmauri_signing_rsa
```

## Quickstart

The example below generates an RSA key, signs a JSON envelope, and then verifies
the detached signature using the corresponding public key. The same pattern
applies to raw byte payloads via `sign_bytes`/`verify_bytes`.

```python
import asyncio

from cryptography.hazmat.primitives.asymmetric import rsa

from swarmauri_signing_rsa import RSAEnvelopeSigner


def key_ref_from_private(private_key):
    return {"kind": "cryptography_obj", "obj": private_key}


def key_ref_from_public(public_key):
    return {"kind": "cryptography_obj", "obj": public_key}


async def main() -> None:
    signer = RSAEnvelopeSigner()
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    envelope = {"payload": {"msg": "hello"}, "headers": {"alg": "RSA-PSS-SHA256"}}

    signatures = await signer.sign_envelope(
        key_ref_from_private(private_key),
        envelope,
        canon="json",
        alg="RSA-PSS-SHA256",
    )

    is_valid = await signer.verify_envelope(
        envelope,
        signatures,
        opts={"pubkeys": [key_ref_from_public(private_key.public_key())]},
    )

    assert is_valid


asyncio.run(main())
```

## Entry Point

The signer registers under the `swarmauri.signings` entry point as
`RSAEnvelopeSigner` and exposes the same name for the Peagen plugin registry.
