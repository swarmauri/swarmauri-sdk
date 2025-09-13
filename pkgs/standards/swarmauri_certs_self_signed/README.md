<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

# Swarmauri Self-Signed Certificate Builder

Standalone plugin providing utilities to issue self-signed X.509 certificates using the `SelfSignedCertificate` builder.

## Installation

```bash
pip install swarmauri_certs_self_signed
```

## Entry Point

This package registers `SelfSignedCertificate` under the `swarmauri.cert_services` entry point.
