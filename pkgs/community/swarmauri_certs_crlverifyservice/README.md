![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_certs_crlverifyservice/">
        <img src="https://static.pepy.tech/badge/swarmauri_certs_crlverifyservice/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_crlverifyservice/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_crlverifyservice.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_crlverifyservice/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_crlverifyservice/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certs_crlverifyservice" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_crlverifyservice/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certs_crlverifyservice?label=swarmauri_certs_crlverifyservice&color=green" alt="PyPI - swarmauri_certs_crlverifyservice"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri CRL Verify Service

`swarmauri_certs_crlverifyservice` provides `CrlVerifyService`, a Swarmauri certificate service for Certificate Revocation List based X.509 verification. It validates certificate validity windows, compares CRL issuers with certificate issuers, detects revoked serial numbers, and parses certificate metadata for audit and observability workflows.

## Why Swarmauri CRL Verify Service?

Use this package when Swarmauri applications need a lightweight revocation-aware certificate verifier without delegating to an external OCSP responder or CA API. It gives PKI monitoring, certificate deployment checks, and compliance workflows a direct Swarmauri interface for CRL-based RFC 5280 verification.

## FAQ

### Q: Does this package issue or sign certificates?

A: No. CSR creation, self-signed certificate creation, and certificate signing are intentionally outside this service. Use Swarmauri certificate packages such as `swarmauri_certs_x509`, `swarmauri_certs_local_ca`, `swarmauri_certs_acme`, or `swarmauri_certs_cfssl` for issuance workflows.

### Q: What encodings does it accept?

A: The implemented certificate path expects PEM-encoded certificates. CRLs may be PEM or DER because `verify_cert()` falls back to DER CRL loading when PEM CRL parsing fails.

### Q: What does verification return?

A: `verify_cert()` returns validity, reason, subject, issuer, not-before, not-after, and revoked fields. Revoked certificates return `valid=False`, `revoked=True`, and `reason="revoked"`.

### Q: What metadata does parsing return?

A: `parse_cert()` returns serial number, subject, issuer, validity timestamps, signature algorithm, and selected extensions such as basic constraints and key usage when present.

## Features

- `CrlVerifyService` adapter dedicated to revocation-aware verification and parsing.
- Certificate validity-window checks using caller-provided `check_time` or current UTC time.
- CRL issuer matching before revoked serial lookup.
- PEM certificate parsing and PEM/DER CRL parsing through `cryptography`.
- Structured validity metadata, revocation flags, issuers, and extension details.
- Verification-only design that delegates CSR and signing flows to other Swarmauri services.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Prerequisites

- Access to current CRLs for the certificate authorities being checked.
- PEM-encoded leaf certificates.
- PEM or DER CRLs.
- Optional trusted root or intermediate certificates when the caller wants to record issuer context alongside revocation checks.

## Installation

Install with `uv`:

```bash
uv add swarmauri_certs_crlverifyservice
```

Install with `pip`:

```bash
pip install swarmauri_certs_crlverifyservice
```

## Usage

Load a certificate and its corresponding CRL, then validate the revocation status and validity window:

```python
import asyncio
from pathlib import Path

from swarmauri_certs_crlverifyservice import CrlVerifyService


async def main() -> None:
    service = CrlVerifyService()
    verification = await service.verify_cert(
        cert=Path("leaf.pem").read_bytes(),
        crls=[Path("issuer.crl").read_bytes()],
        check_revocation=True,
    )

    if verification["valid"]:
        print("Certificate is valid.")
    elif verification.get("revoked"):
        print("Certificate was revoked:", verification["reason"])
    else:
        print("Certificate failed validation:", verification["reason"])


asyncio.run(main())
```

Parse certificate metadata for logging, auditing, or dashboards:

```python
import asyncio
from pathlib import Path

from swarmauri_certs_crlverifyservice import CrlVerifyService


async def main() -> None:
    service = CrlVerifyService()
    metadata = await service.parse_cert(Path("leaf.pem").read_bytes())

    print("Subject:", metadata["subject"])
    print("Valid until:", metadata["not_after"])
    print("Key usage:", metadata.get("key_usage"))


asyncio.run(main())
```

## Related Packages

Certificate service packages:

- [swarmauri_certs_ocspverify](https://pypi.org/project/swarmauri_certs_ocspverify/)
- [swarmauri_certs_x509](https://pypi.org/project/swarmauri_certs_x509/)
- [swarmauri_certs_local_ca](https://pypi.org/project/swarmauri_certs_local_ca/)
- [swarmauri_certs_self_signed](https://pypi.org/project/swarmauri_certs_self_signed/)
- [swarmauri_certs_acme](https://pypi.org/project/swarmauri_certs_acme/)
- [swarmauri_certs_cfssl](https://pypi.org/project/swarmauri_certs_cfssl/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines certificate-service interfaces.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides certificate service base behavior.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

## Best Practices

- Refresh CRLs frequently; RFC 5280 `nextUpdate` dictates how long a CRL should be considered valid.
- Combine this service with Swarmauri signing services to perform a full lifecycle check from issue to deploy to monitor.
- Cache CRLs in memory or a fast datastore to avoid repeatedly loading or downloading them when calling `verify_cert`.
- Log verification outputs, especially `reason` and `revoked`, to your observability pipeline to catch trust issues early.

## License

Apache-2.0


