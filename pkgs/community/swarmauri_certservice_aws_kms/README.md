![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_certservice_aws_kms/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certservice_aws_kms" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_aws_kms/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_aws_kms.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_aws_kms/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certservice_aws_kms" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_aws_kms/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certservice_aws_kms" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_aws_kms/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certservice_aws_kms?label=swarmauri_certservice_aws_kms&color=green" alt="PyPI - swarmauri_certservice_aws_kms"/></a>

</p>

---

# swarmauri_certservice_aws_kms

AWS KMS backed certificate service for Swarmauri.

This package provides an implementation of `CertServiceBase` that signs and verifies X.509 certificates using AWS Key Management Service.

## Features

- Create CSRs from exportable key material.
- Issue certificates using AWS KMS `Sign` API.
- Create self‑signed certificates.
- Verify and parse certificates with RFC 5280 compliance.

## Prerequisites
- Python 3.10 or newer.
- AWS account with KMS keys that allow the `Sign` operation (`RSA` or `ECC_NIST_P256`).
- `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` (or an IAM role/instance profile) granting `kms:GetPublicKey` and `kms:Sign` permissions.
- `boto3` installed (automatically pulled in via this package) and network access to the target AWS region.
- For certificate signing: an issuer subject template and optional CA certificate bytes to embed in verification metadata.

## Extras

- `docs`: documentation helpers.
- `perf`: benchmarking support.

## Installation

```bash
# pip
pip install swarmauri_certservice_aws_kms

# poetry
poetry add swarmauri_certservice_aws_kms

# uv (pyproject-based projects)
uv add swarmauri_certservice_aws_kms
```

## Testing

Run unit, functional and performance tests in isolation from the repository root:

```bash
uv run --package swarmauri_certservice_aws_kms --directory community/swarmauri_certservice_aws_kms pytest
```

## Quickstart: Issue a Certificate with AWS KMS

The snippet below signs an incoming CSR using a customer-managed KMS key. Attach the key ARN to the `KeyRef` via `kid` or `tags` (`aws_kms_key_id`).

```python
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

from swarmauri_certservice_aws_kms import AwsKmsCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = AwsKmsCertService(region_name="us-east-1")

    csr_bytes = Path("tenant.csr").read_bytes()
    ca_cert = Path("ca.pem").read_bytes()

    kms_key = KeyRef(kid="arn:aws:kms:us-east-1:123456789012:key/abcd-1234")

    certificate_pem = await service.sign_cert(
        csr=csr_bytes,
        ca_key=kms_key,
        issuer={"CN": "Example KMS Issuing CA", "O": "Example Corp"},
        ca_cert=ca_cert,
        not_after=int((datetime.now(timezone.utc) + timedelta(days=365)).timestamp()),
    )

    Path("tenant.pem").write_bytes(certificate_pem)
    print("Issued certificate saved to tenant.pem")


if __name__ == "__main__":
    asyncio.run(main())
```

## Generating CSRs and Self-Signed Roots

`AwsKmsCertService` can build CSRs from exportable key material and mint a self-signed certificate using the same KMS key.

```python
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

from swarmauri_certservice_aws_kms import AwsKmsCertService
from swarmauri_core.crypto.types import KeyRef


async def bootstrap_ca() -> None:
    service = AwsKmsCertService(region_name="us-east-1")

    # Generate CSR from a local private key
    key_ref = KeyRef(material=Path("intermediate-key.pem").read_bytes())
    csr_pem = await service.create_csr(
        key=key_ref,
        subject={"CN": "Example Intermediate CA", "O": "Example Corp"},
        san={"dns": ["intermediate.example.com"]},
    )
    Path("intermediate.csr").write_bytes(csr_pem)

    # Issue a self-signed root using a KMS key
    kms_key = KeyRef(kid="arn:aws:kms:us-east-1:123456789012:key/root-ca-key")
    root_pem = await service.create_self_signed(
        key=kms_key,
        subject={"CN": "Example Root CA", "O": "Example Corp"},
        not_after=int((datetime.now(timezone.utc) + timedelta(days=3650)).timestamp()),
    )
    Path("root-ca.pem").write_bytes(root_pem)


if __name__ == "__main__":
    asyncio.run(bootstrap_ca())
```

## Best Practices
- Grant the KMS key limited permissions: `kms:GetPublicKey`, `kms:DescribeKey`, `kms:Sign`. Avoid broad grants (e.g., wildcard actions).
- Store KMS key ARNs in `KeyRef.tags["aws_kms_key_id"]` or `KeyRef.kid` for clarity and to avoid hard-coding ARNs throughout application logic.
- Coordinate certificate validity with KMS key rotation—renew certificates before rotating customer-managed keys.
- Cache returned certificates and metadata to minimize repeated calls to KMS and reduce signing latency.
