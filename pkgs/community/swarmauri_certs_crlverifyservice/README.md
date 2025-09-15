![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_certs_crlverifyservice/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certs_crlverifyservice" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_crlverifyservice/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_crlverifyservice.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_crlverifyservice/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certs_crlverifyservice" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_crlverifyservice/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certs_crlverifyservice" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_crlverifyservice/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certs_crlverifyservice?label=swarmauri_certs_crlverifyservice&color=green" alt="PyPI - swarmauri_certs_crlverifyservice"/></a>
</p>

---

# swarmauri_certs_crlverifyservice

CRL-based certificate verification service for the Swarmauri SDK.

This package implements an ``ICertService`` that checks X.509 certificates
against Certificate Revocation Lists as described in
[RFC 5280](https://www.rfc-editor.org/rfc/rfc5280). It validates the
certificate's validity period, issuer, and revocation status.

## Features
- Verify certificate validity and revocation using provided CRLs.
- Parse PEM certificates to extract basic metadata and common extensions.

## Installation
```bash
pip install swarmauri_certs_crlverifyservice
```

## Usage
```python
from swarmauri_certs_crlverifyservice import CrlVerifyService

svc = CrlVerifyService()
result = await svc.verify_cert(cert_bytes, crls=[crl_bytes])
meta = await svc.parse_cert(cert_bytes)
```

