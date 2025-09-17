![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_certs_x509verify/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certs_x509verify" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_certs_x509verify/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_certs_x509verify.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_x509verify/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certs_x509verify" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_x509verify/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certs_x509verify" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_x509verify/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certs_x509verify?label=swarmauri_certs_x509verify&color=green" alt="PyPI - swarmauri_certs_x509verify"/></a>
</p>

---

# Swarmauri Certs X509 Verify

An asynchronous X.509 certificate verification and parsing service
implementing `CertServiceBase` for the Swarmauri ecosystem. The
`X509VerifyService` works with PEM or DER encoded certificates to surface
metadata and perform lightweight trust checks suitable for development
and integration testing.

## Features

- Async-first interface exposing `verify_cert` and `parse_cert` coroutines.
- Accepts PEM or DER encoded certificates without additional tooling.
- `parse_cert` extracts the serial number, issuer, subject, validity
  window, signature algorithm, Subject Alternative Names (SAN) and
  Extended Key Usage (EKU) values.
- `verify_cert` performs a timestamp check and one-hop signature
  validation against provided trust roots or intermediates.
- Designed for basic validation flows – revocation checking and complex
  path building are intentionally out of scope and reported as
  `revocation_checked=False` in the response.

## Installation

Install the package with your preferred Python packaging tool:

```bash
pip install swarmauri_certs_x509verify
```

```bash
poetry add swarmauri_certs_x509verify
```

```bash
uv pip install swarmauri_certs_x509verify
```

## Quick start

The example below issues an in-memory self-signed certificate, parses its
metadata and verifies the certificate against itself as a trust root.
Both coroutines are executed with `asyncio.run` for convenience in
scripts and documentation. The resulting dictionary mirrors the values
returned by the service at runtime.

```python
# README example: verify and parse a development certificate
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

from swarmauri_certs_x509verify import X509VerifyService


def issue_dev_certificate() -> bytes:
    private_key = ec.generate_private_key(ec.SECP256R1())
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "example.test")])
    now = datetime.now(timezone.utc)

    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=1))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName("example.test")]),
            critical=False,
        )
        .add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),
            critical=False,
        )
        .sign(private_key=private_key, algorithm=hashes.SHA256())
    )

    return certificate.public_bytes(serialization.Encoding.PEM)


async def main() -> dict[str, dict[str, Any]]:
    certificate_pem = issue_dev_certificate()
    service = X509VerifyService()

    parsed = await service.parse_cert(certificate_pem)
    verification = await service.verify_cert(certificate_pem, trust_roots=[certificate_pem])

    return {"parsed": parsed, "verification": verification}


example_result = asyncio.run(main())
print(example_result["parsed"]["subject"])
print(example_result["verification"]["valid"])
```

`example_result["verification"]["valid"]` resolves to `True` when the
certificate is valid for the supplied timestamp. If the time window fails
or no matching trust root is provided, the service returns
`valid=False` and the `reason` field is set to `"invalid_chain_or_time"`.

## Entry Point

The service registers under the `swarmauri.certs` entry point as
`X509VerifyService` and under `peagen.plugins.certs` as `x509verify`.
