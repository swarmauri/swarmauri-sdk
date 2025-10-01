![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_certs_acme/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certs_acme" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_acme/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_acme.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_acme/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certs_acme" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_acme/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certs_acme" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_acme/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certs_acme?label=swarmauri_certs_acme&color=green" alt="PyPI - swarmauri_certs_acme"/></a>
</p>

---

# Swarmauri ACME Certificate Service

Community plugin providing an ACME (RFC 8555) certificate service built on top of Swarmauri's certificate interfaces.

## Features
- Implements `AcmeCertService`, a drop-in `CertServiceBase` compatible class for Swarmauri workflows.
- Supports ACME directory discovery, order creation, finalization, and full chain retrieval.
- Handles RSA and EC key material while exposing capability metadata through `supports()`.
- Convenience helpers for certificate verification and parsing using `cryptography` primitives.

## Prerequisites
- Python 3.10 or newer.
- Existing ACME account key material (PEM encoded) accessible to your Swarmauri runtime.
- Network access to your chosen ACME directory (defaults to Let's Encrypt production).
- DNS or HTTP challenge automation handled externally; this service focuses on CSR submission and certificate retrieval.

## Installation

```bash
# pip
pip install swarmauri_certs_acme

# poetry
poetry add swarmauri_certs_acme

# uv (pyproject-based projects)
uv add swarmauri_certs_acme
```

## Quickstart

The snippet below submits a CSR to Let's Encrypt using `AcmeCertService` and persists the resulting PEM chain.

```python
import asyncio
from pathlib import Path

from swarmauri_certs_acme import AcmeCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    account_key = KeyRef(material=Path("account-key.pem").read_bytes())

    service = AcmeCertService(
        account_key=account_key,
        contact_emails=["admin@example.com"],
    )

    csr_bytes = Path("server.csr").read_bytes()
    certificate_chain = await service.sign_cert(
        csr=csr_bytes,
        ca_key=account_key,  # required by the CertService interface
    )

    Path("server-fullchain.pem").write_bytes(certificate_chain)
    print("Certificate chain written to server-fullchain.pem")


if __name__ == "__main__":
    asyncio.run(main())
```

## CSR Generation Example

`AcmeCertService` can construct a CSR when provided with private key material and subject metadata:

```python
import asyncio
from pathlib import Path

from swarmauri_certs_acme import AcmeCertService
from swarmauri_core.crypto.types import KeyRef


async def build_csr() -> None:
    account_key = KeyRef(material=Path("account-key.pem").read_bytes())
    host_key = KeyRef(material=Path("server-key.pem").read_bytes())

    service = AcmeCertService(account_key=account_key)

    csr_bytes = await service.create_csr(
        key=host_key,
        subject={"CN": "example.com"},
        san={"dns": ["example.com", "www.example.com"]},
    )
    Path("server.csr").write_bytes(csr_bytes)


if __name__ == "__main__":
    asyncio.run(build_csr())
```

## Verification and Parsing

Use the built-in helpers to inspect returned certificates before deployment:

```python
import asyncio
from pathlib import Path

from swarmauri_certs_acme import AcmeCertService
from swarmauri_core.crypto.types import KeyRef


async def inspect() -> None:
    account_key = KeyRef(material=Path("account-key.pem").read_bytes())
    service = AcmeCertService(account_key=account_key)

    pem_chain = Path("server-fullchain.pem").read_bytes()

    info = await service.verify_cert(pem_chain)
    print("Issuer:", info["issuer"])
    print("Valid until:", info["not_after"])

    metadata = await service.parse_cert(pem_chain)
    print(metadata)


if __name__ == "__main__":
    asyncio.run(inspect())
```

## Best Practices
- Rotate account keys periodically and store them in a secure vault (`KeyRef` works with external KMS integrations).
- When using Let's Encrypt production, respect rate limits and consider staging endpoints during development.
- Automate DNS/HTTP challenges upstream; this service assumes the order is ready for finalization once the CSR is submitted.
- Cache successful certificate chains and perform proactive renewals before `not_after` to avoid downtime.
