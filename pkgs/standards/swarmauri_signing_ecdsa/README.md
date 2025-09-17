![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


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

An asynchronous ECDSA-based signer that implements the `ISigning` interface for
detached signatures over raw bytes and canonicalized envelopes.

## Features

- JSON canonicalization built in, with optional CBOR canonicalization via
  [`cbor2`](https://pypi.org/project/cbor2/)
- Supports the `ECDSA-P256-SHA256`, `ECDSA-P384-SHA384`, and
  `ECDSA-P521-SHA512` curves provided by
  [`cryptography`](https://pypi.org/project/cryptography/)
- Multi-signature aware verification with opt-in algorithm restrictions through
  the `require` mapping
- Detached signature generation for both raw byte payloads and Swarmauri
  envelopes

## Installation

### pip

```bash
pip install swarmauri_signing_ecdsa
# Optional CBOR support
pip install "swarmauri_signing_ecdsa[cbor]"
```

### Poetry

```bash
poetry add swarmauri_signing_ecdsa
# Optional CBOR support
poetry add "swarmauri_signing_ecdsa[cbor]"
```

### uv

```bash
# Install uv if it is not already available on your system
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install the signer package
uv pip install swarmauri_signing_ecdsa
# Optional CBOR support
uv pip install "swarmauri_signing_ecdsa[cbor]"
```

## Usage

The signer operates asynchronously and expects private keys to be supplied via
the `KeyRef` mappings defined in `swarmauri_core`. When verifying, provide the
corresponding public keys through the `opts={"pubkeys": [...]}` option.

```python
import asyncio
from cryptography.hazmat.primitives.asymmetric import ec

from swarmauri_signing_ecdsa import EcdsaEnvelopeSigner


async def main() -> None:
    signer = EcdsaEnvelopeSigner()

    # Provide the private key as a KeyRef understood by swarmauri_core
    private_key = ec.generate_private_key(ec.SECP256R1())
    key_ref = {"kind": "cryptography_obj", "obj": private_key}

    envelope = {
        "headers": {"kid": "example"},
        "payload": {"message": "signed hello"},
    }

    signatures = await signer.sign_envelope(
        key_ref,
        envelope,
        canon="json",
    )

    is_valid = await signer.verify_envelope(
        envelope,
        signatures,
        canon="json",
        opts={"pubkeys": [private_key.public_key()]},
    )

    print(f"Signature valid? {is_valid}")


if __name__ == "__main__":
    asyncio.run(main())
```

## Entry Point

The signer registers under the `swarmauri.signings` entry point as
`EcdsaEnvelopeSigner`.
