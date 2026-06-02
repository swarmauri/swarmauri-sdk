![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_certs_ocspverify/">
        <img src="https://static.pepy.tech/badge/swarmauri_certs_ocspverify/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_ocspverify/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_ocspverify.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_ocspverify/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_ocspverify/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certs_ocspverify" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_ocspverify/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certs_ocspverify?label=swarmauri_certs_ocspverify&color=green" alt="PyPI - swarmauri_certs_ocspverify"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri OCSP Verify Service

`swarmauri_certs_ocspverify` provides `OcspVerifyService`, a Swarmauri certificate service for Online Certificate Status Protocol checks. It reads OCSP responder URLs from the certificate Authority Information Access extension, builds DER OCSP requests with the issuer certificate, posts them with `httpx`, and reports whether the responder returned a GOOD certificate status.

## Why Swarmauri OCSP Verify Service?

Use this package when Swarmauri applications need live revocation checks for PEM X.509 certificates. It keeps OCSP request construction, responder lookup, HTTP submission, status parsing, and basic certificate metadata extraction behind the common Swarmauri certificate-service interface.

## FAQ

### Q: Does this package issue or sign certificates?

A: No. `create_csr()`, `create_self_signed()`, and `sign_cert()` intentionally raise `NotImplementedError`; this service is verification-only.

### Q: What input does OCSP verification require?

A: `verify_cert()` requires the leaf certificate as PEM bytes and the issuer certificate as the first item in `intermediates`. The issuer certificate is required to build the OCSP request.

### Q: What happens when a certificate has no OCSP URL?

A: The service returns `valid=False`, `reason="no_ocsp_url"`, and `ocsp_checked=False`.

### Q: Which standards does this package target?

A: The implementation documents RFC 6960 for OCSP behavior and RFC 5280 for X.509 certificate and Authority Information Access metadata.

## Features

- `OcspVerifyService` class registered under the `swarmauri.certs` entry point.
- OCSP responder URL extraction from the Authority Information Access extension.
- DER OCSP request construction with `cryptography.x509.ocsp.OCSPRequestBuilder`.
- Async HTTP OCSP responder calls through `httpx.AsyncClient`.
- GOOD-status mapping to `valid=True`.
- `this_update` and `next_update` timestamp reporting from OCSP responses.
- Certificate metadata parsing for subject, issuer, not-before, not-after, and OCSP URLs.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Prerequisites

- PEM-encoded leaf certificate to inspect and validate.
- PEM-encoded issuer certificate supplied through `intermediates`.
- Network access to the OCSP responder URL embedded in the leaf certificate.
- Application-level retry, timeout, and cache policy for production revocation checks.

## Installation

Install with `uv`:

```bash
uv add swarmauri_certs_ocspverify
```

Install with `pip`:

```bash
pip install swarmauri_certs_ocspverify
```

## Usage

Perform an OCSP status check for a leaf certificate using its issuer certificate:

```python
import asyncio
from pathlib import Path

from swarmauri_certs_ocspverify import OcspVerifyService


async def main() -> None:
    service = OcspVerifyService()
    verification = await service.verify_cert(
        cert=Path("leaf.pem").read_bytes(),
        intermediates=[Path("issuer.pem").read_bytes()],
        check_revocation=True,
    )

    if verification["valid"]:
        print("Certificate status: GOOD")
    else:
        print("Certificate status:", verification["reason"])
    print("Next update:", verification.get("next_update"))


asyncio.run(main())
```

Inspect certificate metadata and embedded OCSP responder URLs:

```python
import asyncio
from pathlib import Path

from swarmauri_certs_ocspverify import OcspVerifyService


async def main() -> None:
    service = OcspVerifyService()
    metadata = await service.parse_cert(Path("leaf.pem").read_bytes())

    print("Subject:", metadata["subject"])
    print("Issuer:", metadata["issuer"])
    print("OCSP URLs:", metadata.get("ocsp_urls", []))


asyncio.run(main())
```

## Related Packages

Certificate service packages:

- [swarmauri_certs_crlverifyservice](https://pypi.org/project/swarmauri_certs_crlverifyservice/)
- [swarmauri_certs_x509](https://pypi.org/project/swarmauri_certs_x509/)
- [swarmauri_certs_local_ca](https://pypi.org/project/swarmauri_certs_local_ca/)
- [swarmauri_certs_self_signed](https://pypi.org/project/swarmauri_certs_self_signed/)
- [swarmauri_certs_acme](https://pypi.org/project/swarmauri_certs_acme/)
- [swarmauri_certs_cfssl](https://pypi.org/project/swarmauri_certs_cfssl/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines certificate-service interfaces.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides `CertServiceBase`.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) provides standard Swarmauri components for certificate-adjacent workflows.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

## Best Practices

- Cache issuer certificates alongside leaf certificates so OCSP requests can be constructed quickly.
- Respect OCSP responder rate limits and cache GOOD responses until `next_update` when policy allows.
- Combine OCSP checks with CRL fallback for authorities that support multiple revocation mechanisms.
- Log `reason`, `ocsp_checked`, `this_update`, and `next_update` fields for incident response and compliance reporting.

## License

Apache-2.0


