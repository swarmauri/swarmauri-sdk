![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_certservice_gcpkms/">
        <img src="https://static.pepy.tech/badge/swarmauri_certservice_gcpkms/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_gcpkms/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_gcpkms.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_gcpkms/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_gcpkms/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certservice_gcpkms" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_gcpkms/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certservice_gcpkms?label=swarmauri_certservice_gcpkms&color=green" alt="PyPI - swarmauri_certservice_gcpkms"/></a>
</p>

# Swarmauri Google Cloud KMS Certificate Service

`swarmauri_certservice_gcpkms` provides `GcpKmsCertService`, a Swarmauri certificate service for Google Cloud KMS oriented certificate workflows. It creates CSRs, creates self-signed certificates, signs CSRs, verifies certificate validity and signatures, and parses X.509 metadata while resolving signing keys from Google Cloud KMS key-version references.

## Why Swarmauri Google Cloud KMS Certificate Service?

Use this package when Swarmauri certificate workflows need to integrate with Google Cloud KMS key versions while preserving the common `CertServiceBase` interface. The service accepts a caller-provided KMS client or creates `KeyManagementServiceClient`, resolves key versions from `KeyRef`, and uses `cryptography` certificate builders for X.509 output.

## FAQ

### Q: How does the service find the Google Cloud KMS key version?

A: Key versions are resolved from `KeyRef.tags["gcp_kms_key_version"]`, `KeyRef.tags["kms_key_version"]`, or `KeyRef.kid`.

### Q: Does this package install Google Cloud KMS by default?

A: No. The base package keeps Google Cloud KMS optional. Install `swarmauri_certservice_gcpkms[gcp]` when the runtime should create a real `KeyManagementServiceClient`.

### Q: What is the current KMS signing boundary?

A: Certificate operations use an internal `_make_kms_private_key(client, version)` hook to obtain a `cryptography`-compatible private-key object. Tests can patch this hook; production use should provide or extend that adapter for the selected Google Cloud KMS signing flow.

### Q: What certificate operations are implemented?

A: The service implements CSR creation, self-signed certificate creation, CSR signing, signature and validity-window verification, and certificate metadata parsing.

## Features

- `GcpKmsCertService` class registered under the `swarmauri.cert_services` entry point.
- Optional Google Cloud KMS client creation through `google-cloud-kms`.
- Caller-provided client support for tests and custom runtimes.
- Key-version resolution from Swarmauri `KeyRef`.
- CSR creation with subject and DNS/IP SAN support.
- Self-signed certificate creation with KMS-backed private-key adapter.
- CSR signing with issuer metadata and optional extensions.
- Certificate verification against validity window and optional trust root.
- Certificate parsing for version, serial, signature algorithm, issuer, subject, validity, and CA status.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Prerequisites

- Google Cloud project with the Cloud KMS API enabled.
- Application credentials available to Google client libraries.
- KMS key versions with asymmetric signing capability.
- `google-cloud-kms` installed through the `gcp` extra when using the default client.
- A runtime adapter for `_make_kms_private_key` when using live KMS signing.

## Installation

Install with `uv`:

```bash
uv add "swarmauri_certservice_gcpkms[gcp]"
```

Install with `pip`:

```bash
pip install "swarmauri_certservice_gcpkms[gcp]"
```

Install the package without the Google Cloud client when injecting a test or custom client:

```bash
uv add swarmauri_certservice_gcpkms
```

## Usage

Create a service and resolve a KMS key version from `KeyRef`:

```python
from swarmauri_certservice_gcpkms import GcpKmsCertService
from swarmauri_core.crypto.types import KeyRef

service = GcpKmsCertService()
key = KeyRef(
    kid="projects/my-project/locations/us-central1/keyRings/pki/cryptoKeys/root/cryptoKeyVersions/1"
)

print(service.supports()["features"])
```

Generate a CSR:

```python
import asyncio

from swarmauri_certservice_gcpkms import GcpKmsCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = GcpKmsCertService()
    key = KeyRef(
        kid="projects/my-project/locations/us-central1/keyRings/pki/cryptoKeys/leaf/cryptoKeyVersions/1"
    )

    csr = await service.create_csr(
        key=key,
        subject={"CN": "leaf.example.com", "O": "Example Corp"},
        san={"dns": ["leaf.example.com"]},
    )
    print(csr[:40])


asyncio.run(main())
```

Sign a CSR after providing a KMS-compatible signing adapter:

```python
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

from swarmauri_certservice_gcpkms import GcpKmsCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = GcpKmsCertService()
    ca_key = KeyRef(
        kid="projects/my-project/locations/us-central1/keyRings/pki/cryptoKeys/issuing-ca/cryptoKeyVersions/1"
    )

    certificate = await service.sign_cert(
        csr=Path("leaf.csr").read_bytes(),
        ca_key=ca_key,
        issuer={"CN": "Example GCP Issuing CA", "O": "Example Corp"},
        not_after=int((datetime.now(timezone.utc) + timedelta(days=365)).timestamp()),
    )
    Path("leaf.pem").write_bytes(certificate)


asyncio.run(main())
```

## Related Packages

Certificate service packages:

- [swarmauri_certservice_aws_kms](https://pypi.org/project/swarmauri_certservice_aws_kms/)
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

- Use least-privilege IAM roles for Cloud KMS signing operations.
- Store fully qualified key-version names in `KeyRef.kid` or `KeyRef.tags`.
- Validate that the signing adapter matches the KMS key algorithm before issuing certificates.
- Log certificate serials, issuer metadata, and key-version references for auditability.

## License

Apache-2.0
