![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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
