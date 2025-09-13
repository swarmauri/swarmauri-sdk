![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# Swarmauri Certs PKCS#11

A PKCS#11-backed certificate service implementing `CertServiceBase`.
It generates and verifies X.509 certificates using hardware security modules.

## Installation

```bash
pip install swarmauri_certs_pkcs11
```

## Entry Point

The service registers under the `swarmauri.cert_services` entry point as `Pkcs11CertService`.
