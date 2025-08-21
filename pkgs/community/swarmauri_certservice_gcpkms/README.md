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
