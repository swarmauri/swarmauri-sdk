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

## Installation

```bash
pip install swarmauri_certservice_gcpkms[gcp]
```

The optional `gcp` extra installs the `google-cloud-kms` dependency.

## Usage

```python
from swarmauri_certservice_gcpkms import GcpKmsCertService

service = GcpKmsCertService()
# ... use service methods
```

## License

Apache-2.0
