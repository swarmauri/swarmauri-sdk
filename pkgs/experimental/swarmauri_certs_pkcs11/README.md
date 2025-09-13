<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

# Swarmauri Certs PKCS#11

A PKCS#11-backed certificate service implementing `CertServiceBase`.
It generates and verifies X.509 certificates using hardware security modules.

## Installation

```bash
pip install swarmauri_certs_pkcs11
```

## Entry Point

The service registers under the `swarmauri.cert_services` entry point as `Pkcs11CertService`.
