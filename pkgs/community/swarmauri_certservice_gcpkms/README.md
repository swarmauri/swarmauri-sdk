![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

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

## Installation

```bash
pip install swarmauri_certservice_gcpkms[gcp]
```

The optional `gcp` extra installs the `google-cloud-kms` dependency.

## Usage

```python
import asyncio
from swarmauri_certservice_gcpkms import GcpKmsCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = GcpKmsCertService()
    key = KeyRef(kid="projects/PROJECT_ID/locations/LOC/keyRings/RING/cryptoKeys/KEY/cryptoKeyVersions/1")
    subject = {"CN": "example.com"}
    csr = await service.create_csr(key=key, subject=subject)
    print(csr.decode())


asyncio.run(main())
```

## License

Apache-2.0
