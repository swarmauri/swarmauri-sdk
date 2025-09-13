![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# Swarmauri Self-Signed Certificate Builder

Standalone plugin providing utilities to issue self-signed X.509 certificates using the `SelfSignedCertificate` builder.

## Installation

```bash
pip install swarmauri_certs_self_signed
```

## Entry Point

This package registers `SelfSignedCertificate` under the `swarmauri.cert_services` entry point.
