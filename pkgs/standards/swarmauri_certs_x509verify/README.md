![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

# Swarmauri Certs X509 Verify

A verification-only service for X.509 certificates implementing
`CertServiceBase`.

Features:
- Parse certificates for subject, issuer, SAN, EKU and validity times.
- Basic chain validation and time checks.

## Installation

```bash
pip install swarmauri_certs_x509verify
```

## Usage

```python
from swarmauri_certs_x509verify import X509VerifyService

service = X509VerifyService()
```

## Entry Point

The service registers under the `swarmauri.certs` entry point as
`X509VerifyService`.
