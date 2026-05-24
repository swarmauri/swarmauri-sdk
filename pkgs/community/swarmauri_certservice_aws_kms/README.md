![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_certservice_aws_kms/">
        <img src="https://static.pepy.tech/badge/swarmauri_certservice_aws_kms/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_aws_kms/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_aws_kms.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_aws_kms/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_aws_kms/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certservice_aws_kms" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_aws_kms/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certservice_aws_kms?label=swarmauri_certservice_aws_kms&color=green" alt="PyPI - swarmauri_certservice_aws_kms"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri AWS KMS Certificate Service

`swarmauri_certservice_aws_kms` provides `AwsKmsCertService`, a Swarmauri certificate service that signs X.509 certificate structures with AWS Key Management Service. It creates CSRs from exportable PEM keys, signs incoming PKCS#10 CSRs through AWS KMS `Sign`, creates self-signed CA certificates with KMS-backed keys, verifies issued certificates against trusted issuers, and parses X.509 metadata.

## Why Swarmauri AWS KMS Certificate Service?

Use this package when certificate private keys should remain in AWS KMS while Swarmauri applications still need certificate issuance and verification workflows. The service maps Swarmauri `KeyRef` objects to AWS KMS KeyIds, supports KMS public-key retrieval, assembles X.509 certificates locally, and delegates signing operations to KMS.

## FAQ

### Q: How does the service find the AWS KMS key?

A: `sign_cert()` and `create_self_signed()` resolve the KMS KeyId from `KeyRef.tags["aws_kms_key_id"]`, `KeyRef.tags["kms_key_id"]`, or `KeyRef.kid`.

### Q: Does CSR creation use AWS KMS?

A: No. `create_csr()` requires exportable private key material in `KeyRef.material`. AWS KMS is used for certificate signing and self-signed certificate signatures.

### Q: Which signature algorithms are supported?

A: The service supports RSA-PSS-SHA256, RSA-SHA256, and ECDSA-P256-SHA256 mappings to AWS KMS signing algorithms.

### Q: Can it verify certificates?

A: Yes. `verify_cert()` checks the validity window and, when an issuer certificate is provided through `intermediates` or `trust_roots`, verifies RSA PKCS#1, RSA-PSS, or ECDSA signatures with the issuer public key.

## Features

- `AwsKmsCertService` class registered under the `swarmauri.cert_services` entry point.
- AWS KMS client creation with optional region, endpoint URL, and boto3 session.
- CSR creation from exportable PEM private keys.
- CSR signing with KMS-backed issuer keys.
- Self-signed certificate creation with KMS-backed keys.
- KMS public-key retrieval for issuer SubjectPublicKeyInfo, SKID, and AKID.
- KeyId resolution from Swarmauri `KeyRef` fields.
- PEM and DER certificate output.
- X.509 certificate parsing for subject, issuer, serial, validity, SANs, key usage, EKU, and CA metadata.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Prerequisites

- AWS credentials available to boto3 through environment variables, profiles, IAM role, or workload identity.
- AWS KMS keys that allow `kms:GetPublicKey` and `kms:Sign`.
- KMS key specs compatible with the selected signature algorithm.
- Exportable PEM private key material when using `create_csr()`.
- Issuer subject metadata or CA certificate bytes when signing CSRs.

## Installation

Install with `uv`:

```bash
uv add swarmauri_certservice_aws_kms
```

Install with `pip`:

```bash
pip install swarmauri_certservice_aws_kms
```

## Usage

Sign an incoming CSR using a customer-managed AWS KMS key:

```python
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

from swarmauri_certservice_aws_kms import AwsKmsCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = AwsKmsCertService(region_name="us-east-1")
    kms_key = KeyRef(
        kid="arn:aws:kms:us-east-1:123456789012:key/abcd-1234",
    )

    certificate = await service.sign_cert(
        csr=Path("tenant.csr").read_bytes(),
        ca_key=kms_key,
        issuer={"CN": "Example KMS Issuing CA", "O": "Example Corp"},
        not_after=int((datetime.now(timezone.utc) + timedelta(days=365)).timestamp()),
    )
    Path("tenant.pem").write_bytes(certificate)


asyncio.run(main())
```

Create a CSR from exportable key material:

```python
import asyncio
from pathlib import Path

from swarmauri_certservice_aws_kms import AwsKmsCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = AwsKmsCertService(region_name="us-east-1")
    csr = await service.create_csr(
        key=KeyRef(material=Path("intermediate-key.pem").read_bytes()),
        subject={"CN": "Example Intermediate CA", "O": "Example Corp"},
        san={"dns": ["intermediate.example.com"]},
    )
    Path("intermediate.csr").write_bytes(csr)


asyncio.run(main())
```

Create a self-signed root with a KMS-backed key:

```python
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

from swarmauri_certservice_aws_kms import AwsKmsCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = AwsKmsCertService(region_name="us-east-1")
    kms_key = KeyRef(kid="arn:aws:kms:us-east-1:123456789012:key/root-ca-key")

    root = await service.create_self_signed(
        key=kms_key,
        subject={"CN": "Example Root CA", "O": "Example Corp"},
        not_after=int((datetime.now(timezone.utc) + timedelta(days=3650)).timestamp()),
    )
    Path("root-ca.pem").write_bytes(root)


asyncio.run(main())
```

## Related Packages

Certificate service packages:

- [swarmauri_certservice_gcpkms](https://pypi.org/project/swarmauri_certservice_gcpkms/)
- [swarmauri_certservice_stepca](https://pypi.org/project/swarmauri_certservice_stepca/)
- [swarmauri_certs_azure](https://pypi.org/project/swarmauri_certs_azure/)
- [swarmauri_certs_local_ca](https://pypi.org/project/swarmauri_certs_local_ca/)
- [swarmauri_certs_x509](https://pypi.org/project/swarmauri_certs_x509/)
- [swarmauri_certs_cfssl](https://pypi.org/project/swarmauri_certs_cfssl/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines certificate interfaces and `KeyRef`.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides `CertServiceBase` and component registration.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) provides standard Swarmauri components for certificate-adjacent workflows.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

## Best Practices

- Grant the KMS key limited permissions: `kms:GetPublicKey`, `kms:DescribeKey`, and `kms:Sign`.
- Store KMS key ARNs in `KeyRef.tags["aws_kms_key_id"]` or `KeyRef.kid` instead of scattering ARNs through application code.
- Coordinate certificate validity with KMS key rotation and renew certificates before rotating customer-managed keys.
- Cache parsed certificate metadata and issued certificates to reduce repeated KMS signing calls.

## License

Apache-2.0


