![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_certs_crlverifyservice/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certs_crlverifyservice" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_crlverifyservice/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_crlverifyservice.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_crlverifyservice/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certs_crlverifyservice" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_crlverifyservice/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certs_crlverifyservice" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_crlverifyservice/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certs_crlverifyservice?label=swarmauri_certs_crlverifyservice&color=green" alt="PyPI - swarmauri_certs_crlverifyservice"/></a>
</p>

---

# swarmauri_certs_crlverifyservice

CRL-based certificate verification service for the Swarmauri SDK.

This package implements an `ICertService` that checks X.509 certificates
against Certificate Revocation Lists as described in
[RFC 5280](https://www.rfc-editor.org/rfc/rfc5280). It validates the
certificate's validity period, issuer, and revocation status.

## Features
- `CrlVerifyService` adapter dedicated to revocation-aware verification and parsing.
- Accepts PEM or DER certificates/CRLs and normalizes them with `cryptography`.
- Returns structured validity metadata, revocation flags, issuers, and extension details.
- Focuses purely on verification; CSR and signing flows stay delegated to other Swarmauri services.

## Prerequisites
- Python 3.10 or newer.
- Access to up-to-date CRLs for the certificate authorities you care about.
- Certificates and CRLs stored in PEM (Base64) or DER; the service can decode either.
- Optional: trusted root/intermediate certificates if you plan to record issuer context alongside revocation checks.

## Installation

```bash
# pip
pip install swarmauri_certs_crlverifyservice

# poetry
poetry add swarmauri_certs_crlverifyservice

# uv (pyproject-based projects)
uv add swarmauri_certs_crlverifyservice
```

## Quickstart: Revocation Check

Load a certificate and its corresponding CRL, then validate the revocation status and validity window:

```python
import asyncio
from pathlib import Path

from swarmauri_certs_crlverifyservice import CrlVerifyService


async def main() -> None:
    service = CrlVerifyService()

    cert_bytes = Path("leaf.pem").read_bytes()
    crl_bytes = Path("issuer.crl").read_bytes()

    verification = await service.verify_cert(
        cert=cert_bytes,
        crls=[crl_bytes],
        check_revocation=True,
    )

    if verification["valid"]:
        print("Certificate is valid.")
    elif verification.get("revoked"):
        print("Certificate was revoked:", verification["reason"])
    else:
        print("Certificate failed validation:", verification["reason"])


if __name__ == "__main__":
    asyncio.run(main())
```

## Parsing Metadata

Use `parse_cert` to surface fields needed for logging, auditing, or dashboards:

```python
import asyncio
from pathlib import Path

from swarmauri_certs_crlverifyservice import CrlVerifyService


async def describe() -> None:
    service = CrlVerifyService()
    cert_bytes = Path("leaf.pem").read_bytes()

    metadata = await service.parse_cert(cert_bytes)
    print("Subject:", metadata["subject"])
    print("Valid until:", metadata["not_after"])
    print("Key usage:", metadata.get("key_usage"))


if __name__ == "__main__":
    asyncio.run(describe())
```

## Best Practices
- Refresh CRLs frequently; RFC 5280 `nextUpdate` dictates how long a CRL should be considered valid.
- Combine this service with Swarmauri signing services to perform a full lifecycle check (issue → deploy → monitor).
- Cache CRLs in memory or a fast datastore to avoid repeatedly downloading them when calling `verify_cert`.
- Log verification outputs (especially `reason` and `revoked`) to your observability pipeline to catch trust issues early.
