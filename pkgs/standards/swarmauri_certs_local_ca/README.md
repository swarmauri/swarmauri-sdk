![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_certs_local_ca/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certs_local_ca" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_certs_local_ca/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_certs_local_ca.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_local_ca/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certs_local_ca" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_local_ca/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certs_local_ca" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_local_ca/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certs_local_ca?label=swarmauri_certs_local_ca&color=green" alt="PyPI - swarmauri_certs_local_ca"/></a>
</p>

---

# Swarmauri Certs Local CA

A local certificate authority implementing the `ICertService` interface for issuing and verifying X.509 certificates. Useful for development and testing environments where you need to bootstrap a private PKI quickly.

## Features

- Generate CSRs with optional subject alternative names and certificate extensions.
- Create self-signed CA certificates with sensible defaults (1-year validity, CA basic constraints).
- Sign CSRs to produce leaf certificates, returning PEM or DER output.
- Perform basic certificate verification that ensures the certificate is currently valid and reports issuer/subject metadata.
- Parse certificates to extract key metadata and extension object identifiers.

> **Note:** `verify_cert` only evaluates validity windows; it does not build trust chains or check revocation lists.

## Supported algorithms

`LocalCaCertService.supports()` reports the following capabilities:

- **Key algorithms:** `RSA-2048`, `RSA-3072`, `EC-P256`, `Ed25519`
- **Signature algorithms:** `RSA-PSS-SHA256`, `ECDSA-P256-SHA256`, `Ed25519`
- **Features:** CSR creation, self-signed issuance, CSR signing, verification, and parsing

## Installation

Install the package with your preferred Python packaging tool:

```bash
pip install swarmauri_certs_local_ca
```

```bash
poetry add swarmauri_certs_local_ca
```

If you use [uv](https://docs.astral.sh/uv/), install it first (for example with `pip install uv`) and then add the package:

```bash
uv pip install swarmauri_certs_local_ca
```

## Usage

Below is a minimal end‑to‑end example that issues and verifies a leaf
certificate signed by a local certificate authority.  The helper function
`_key` creates the ``KeyRef`` objects required by the service.

```python
import asyncio
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from swarmauri_certs_local_ca import LocalCaCertService
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse


def _key(name: str) -> KeyRef:
    sk = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = sk.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    return KeyRef(
        kid=name,
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=pem,
    )


async def main() -> None:
    svc = LocalCaCertService()
    ca_key = _key("ca")
    leaf_key = _key("leaf")

    # Create a certificate signing request for the leaf key.
    csr = await svc.create_csr(leaf_key, {"CN": "leaf"})

    # Sign the CSR with the CA key to produce a leaf certificate.
    cert = await svc.sign_cert(csr, ca_key, issuer={"CN": "ca"})

    # Verify the newly issued certificate.
    result = await svc.verify_cert(cert)
    print(result["valid"], result["subject"], result["issuer"])


asyncio.run(main())
```

`verify_cert` returns a dictionary containing the validity flag plus the RFC 4514
representations of the subject and issuer.  For CA bootstrapping you can call
`create_self_signed` to generate a root certificate and use `parse_cert` to
inspect serial numbers, validity windows, and extension object identifiers.

## Entry Point

The service registers under the `swarmauri.cert_services` entry point as `LocalCaCertService`.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.