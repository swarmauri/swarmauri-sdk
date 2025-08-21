![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

# Swarmauri CertService LocalCA

A local certificate authority implementing the `ICertService` interface for issuing and verifying X.509 certificates. Useful for development and testing environments.

Features:
- CSR generation with subject alternative names
- Self-signed certificate issuance
- Signing CSRs to produce leaf certificates
- Basic certificate verification and parsing
- Optional IDNA support for internationalized DNS names

## Installation

```bash
pip install swarmauri_certservice_localca
```

## Usage

```python
from swarmauri_certservice_localca import LocalCaCertService

svc = LocalCaCertService()
# create a KeyRef for a private key; see swarmauri_core for details
```

## Entry Point

The service registers under the `swarmauri.cert_services` entry point as `LocalCaCertService`.
