![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

# Swarmauri Certs PKCS#11

A PKCS#11-backed certificate service implementing `CertServiceBase`.
It generates and verifies X.509 certificates using hardware security modules.

## Installation

```bash
pip install swarmauri_certs_pkcs11
```

## Entry Point

The service registers under the `swarmauri.cert_services` entry point as `Pkcs11CertService`.
