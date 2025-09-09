<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
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
