![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_signing_ca/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_signing_ca" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_ca/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_ca.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_ca/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_signing_ca" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_ca/">
        <img src="https://img.shields.io/pypi/l/swarmauri_signing_ca" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_ca/">
        <img src="https://img.shields.io/pypi/v/swarmauri_signing_ca?label=swarmauri_signing_ca&color=green" alt="PyPI - swarmauri_signing_ca"/></a>
</p>

---

# Swarmauri Signing CA

`swarmauri_signing_ca` exposes a certificate-authority-capable implementation of
`ISigning` that focuses on detached signatures over raw bytes and canonicalized
Swarmauri envelopes. The signer understands common public key algorithms and ships
with utilities for issuing and validating X.509 material.

## Highlights

- Deterministic JSON canonicalization for envelopes (JSON is the supported canon).
- Detached signature support for Ed25519, ECDSA (P-256 and compatible curves), and RSA-PSS/RS256.
- Accepts PEM-encoded private keys or pre-instantiated cryptography objects via `KeyRef`.
- X.509 helpers for issuing self-signed certificates, signing CSRs, and verifying simple chains.
- Advertises the `multi`, `detached_only`, and `x509` features under the `swarmauri.signings` entry point as `CASigner`.

## Installation

Choose the tool that fits your workflow:

```bash
# pip
pip install swarmauri_signing_ca

# Poetry
poetry add swarmauri_signing_ca

# uv
uv add swarmauri_signing_ca
```

## Quickstart

The example below generates an Ed25519 key, signs a message, and verifies the
signature using the same public key. It mirrors what `CASigner` performs in
production environments.

```python
import asyncio

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse
from swarmauri_signing_ca import CASigner


async def main() -> None:
    signer = CASigner()

    private_key = ed25519.Ed25519PrivateKey.generate()
    key_ref = KeyRef(
        kid="demo-ed25519",
        version=1,
        type=KeyType.ED25519,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ),
    )

    message = b"trust but verify"
    signatures = await signer.sign_bytes(key_ref, message)
    signature = signatures[0]

    verified = await signer.verify_bytes(
        message,
        signatures,
        opts={"pubkeys": [private_key.public_key()]},
    )

    print("Signature algorithm:", signature["alg"])
    print("Key fingerprint:", key_ref.fingerprint)
    print("Signature valid:", verified)

    assert verified is True


if __name__ == "__main__":
    asyncio.run(main())
```

### Notes on verification

`CASigner.verify_bytes` expects the caller to provide one or more verification
keys via `opts={"pubkeys": [...]}`. Entries may be `cryptography` public-key
objects or PEM-encoded bytes. The signer reports success as soon as the required
number of signatures validates against the supplied key material.

### X.509 utilities

Beyond detached signatures, `CASigner` assists with certificate authority tasks:

- `issue_self_signed` – build a CA or leaf certificate directly from a
  `KeyRef` and subject mapping.
- `create_csr` – generate a certificate signing request complete with SAN and
  key-usage extensions.
- `sign_csr` – issue certificates from CSRs using an existing CA key and
  certificate chain.
- `verify_chain` – validate a leaf against an intermediate chain and optional
  trust anchors with basic time and CA checks.

These helpers rely on the same key-loading logic demonstrated in the quickstart,
so PEM-encoded keys or `KeyRef.tags["crypto_obj"]` objects both work seamlessly.

## Entry Point

The signer registers under the `swarmauri.signings` entry point as `CASigner` and
can be resolved through the Swarmauri plugin manager alongside other signing
implementations.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.