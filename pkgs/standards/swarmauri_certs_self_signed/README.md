![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

# Swarmauri Self-Signed Certificate Builder

Standalone plugin providing utilities to issue self-signed X.509 certificates using the `SelfSignedCertificate` builder.

## Installation

```bash
pip install swarmauri_certs_self_signed
```

## Entry Point

This package registers `SelfSignedCertificate` under the `swarmauri.cert_services` entry point.
