![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_certs_ocspverify/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certs_ocspverify" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_ocspverify/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_ocspverify.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_ocspverify/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certs_ocspverify" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_ocspverify/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certs_ocspverify" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_ocspverify/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certs_ocspverify?label=swarmauri_certs_ocspverify&color=green" alt="PyPI - swarmauri_certs_ocspverify"/></a>

</p>

---

# swarmauri_certs_ocspverify

OCSP-based certificate verification service for the Swarmauri SDK.

This package provides an implementation of an `ICertService` that checks
certificate revocation status using the Online Certificate Status Protocol
(OCSP) defined in [RFC 6960](https://www.rfc-editor.org/rfc/rfc6960) while
remaining compatible with X.509 certificate guidelines from
[RFC 5280](https://www.rfc-editor.org/rfc/rfc5280).

## Features
- Parse PEM certificates to extract subject, issuer and OCSP responder URLs.
- Verify certificate status via OCSP responders advertised in the certificate's
  Authority Information Access extension.

## Prerequisites
- Python 3.10 or newer.
- Leaf certificate PEM to inspect and validate.
- Issuer (intermediate) certificate PEM required to build the OCSP request.
- Network access to the OCSP responder URLs exposed in the certificate's Authority Information Access extension.
- Optional: trust root bundle if performing additional validation on issuer metadata alongside OCSP results.

## Installation

```bash
# pip
pip install swarmauri_certs_ocspverify

# poetry
poetry add swarmauri_certs_ocspverify

# uv (pyproject-based projects)
uv add swarmauri_certs_ocspverify
```

## Usage

Perform an OCSP status check for a leaf certificate using its issuer certificate:

```python
import asyncio
from pathlib import Path

from swarmauri_certs_ocspverify import OcspVerifyService


async def main() -> None:
    service = OcspVerifyService()

    leaf_cert = Path("leaf.pem").read_bytes()
    issuer_cert = Path("issuer.pem").read_bytes()

    verification = await service.verify_cert(
        cert=leaf_cert,
        intermediates=[issuer_cert],
        check_revocation=True,
    )

    if verification["valid"]:
        print("Certificate status: GOOD")
    else:
        print("Certificate status:", verification["reason"])
    print("Next update:", verification.get("next_update"))


if __name__ == "__main__":
    asyncio.run(main())
```

## Parsing OCSP Metadata

Use `parse_cert` to confirm which OCSP responder URLs are embedded and to inspect the validity window:

```python
import asyncio
from pathlib import Path

from swarmauri_certs_ocspverify import OcspVerifyService


async def describe() -> None:
    service = OcspVerifyService()
    leaf_cert = Path("leaf.pem").read_bytes()

    metadata = await service.parse_cert(leaf_cert)
    print("Subject:", metadata["subject"])
    print("Issuer:", metadata["issuer"])
    print("OCSP URLs:", metadata.get("ocsp_urls", []))


if __name__ == "__main__":
    asyncio.run(describe())
```

## Best Practices
- Cache issuer certificates alongside leaf certificates so OCSP requests can be constructed quickly.
- Respect OCSP responder rate limits; consider backoff and caching GOOD responses until `next_update`.
- Combine OCSP checks with CRL fallbacks for authorities that support multiple revocation mechanisms.
- Log `reason` and timestamp fields from the verification output to aid in incident response and compliance reporting.
