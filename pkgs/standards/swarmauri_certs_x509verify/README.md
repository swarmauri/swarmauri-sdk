<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

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
