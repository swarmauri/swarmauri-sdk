![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_certs_x509verify/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certs_x509verify" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_certs_x509verify/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_certs_x509verify.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_x509verify/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certs_x509verify" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_x509verify/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certs_x509verify" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_x509verify/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certs_x509verify?label=swarmauri_certs_x509verify&color=green" alt="PyPI - swarmauri_certs_x509verify"/></a>
</p>

---

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
