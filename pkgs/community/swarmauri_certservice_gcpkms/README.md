![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_certservice_gcpkms/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certservice_gcpkms" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_gcpkms/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_gcpkms.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_gcpkms/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certservice_gcpkms" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_gcpkms/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certservice_gcpkms" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_gcpkms/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certservice_gcpkms?label=swarmauri_certservice_gcpkms&color=green" alt="PyPI - swarmauri_certservice_gcpkms"/></a>

</p>

---

# swarmauri_certservice_gcpkms

Google Cloud KMS backed certificate service for Swarmauri.

This package exposes a `GcpKmsCertService` component implementing
`CertServiceBase`.  It can create CSRs, generate self-signed certificates,
issue certificates from CSRs, verify certificates and parse their
metadata while using keys stored in Google Cloud KMS.

## Features

- Create certificate signing requests using keys stored in KMS
- Issue self-signed or CA-signed certificates
- Verify signatures and validity windows
- Parse certificate metadata including extensions

## Prerequisites

- A Google Cloud project with the Cloud KMS API enabled
- Credentials available to the application (for example via the
  `GOOGLE_APPLICATION_CREDENTIALS` environment variable)
- Keys provisioned in Cloud KMS with the `AsymmetricSign` capability (RSA 2048, EC P-256, or Ed25519).
- Python 3.10 or newer and the `google-cloud-kms` dependency (installed via the extras shown below).
- Network access to the Google Cloud KMS endpoint for the target location.

## Installation

```bash
# pip
pip install swarmauri_certservice_gcpkms[gcp]

# poetry
poetry add swarmauri_certservice_gcpkms -E gcp

# uv (pyproject-based projects)
uv add "swarmauri_certservice_gcpkms[gcp]"
```

The optional `gcp` extra installs the `google-cloud-kms` dependency.

## Usage

### Issue a Certificate from a CSR

```python
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

from swarmauri_certservice_gcpkms import GcpKmsCertService
from swarmauri_core.crypto.types import KeyRef


async def issue_certificate() -> None:
    service = GcpKmsCertService()

    csr_bytes = Path("leaf.csr").read_bytes()
    kms_ca_key = KeyRef(
        kid="projects/my-project/locations/us-central1/keyRings/pki/cryptoKeys/issuing-ca/cryptoKeyVersions/1"
    )

    certificate_pem = await service.sign_cert(
        csr=csr_bytes,
        ca_key=kms_ca_key,
        issuer={"CN": "Example GCP Issuing CA", "O": "Example Corp"},
        not_after=int((datetime.now(timezone.utc) + timedelta(days=365)).timestamp()),
    )

    Path("leaf.pem").write_bytes(certificate_pem)
    print("Issued certificate saved to leaf.pem")


if __name__ == "__main__":
    asyncio.run(issue_certificate())
```

### Create CSRs and Self-Signed Roots

```python
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

from swarmauri_certservice_gcpkms import GcpKmsCertService
from swarmauri_core.crypto.types import KeyRef


async def bootstrap_pki() -> None:
    service = GcpKmsCertService()

    # Generate a CSR using an exportable private key
    local_key = KeyRef(material=Path("intermediate-key.pem").read_bytes())
    csr_pem = await service.create_csr(
        key=local_key,
        subject={"CN": "Intermediate CA", "O": "Example Corp"},
        san={"dns": ["intermediate.example.com"]},
    )
    Path("intermediate.csr").write_bytes(csr_pem)

    # Create a self-signed root using Cloud KMS
    root_key = KeyRef(
        kid="projects/my-project/locations/us-central1/keyRings/pki/cryptoKeys/root-ca/cryptoKeyVersions/1"
    )
    root_pem = await service.create_self_signed(
        key=root_key,
        subject={"CN": "Example Root CA", "O": "Example Corp"},
        not_after=int((datetime.now(timezone.utc) + timedelta(days=3650)).timestamp()),
    )
    Path("root-ca.pem").write_bytes(root_pem)


if __name__ == "__main__":
    asyncio.run(bootstrap_pki())
```

### Verification and Parsing

```python
import asyncio
from pathlib import Path

from swarmauri_certservice_gcpkms import GcpKmsCertService


async def inspect() -> None:
    service = GcpKmsCertService()
    cert_bytes = Path("leaf.pem").read_bytes()
    root_bytes = Path("root-ca.pem").read_bytes()

    verification = await service.verify_cert(
        cert=cert_bytes,
        trust_roots=[root_bytes],
    )
    print("Valid:", verification["valid"], "Issuer:", verification.get("issuer"))

    metadata = await service.parse_cert(cert_bytes)
    print("Subject:", metadata["subject"])
    print("Not after:", metadata["not_after"])


if __name__ == "__main__":
    asyncio.run(inspect())
```

## License

Apache-2.0
