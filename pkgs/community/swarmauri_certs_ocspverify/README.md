![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_certs_ocspverify/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certs_ocspverify" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_ocspverify/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_ocspverify.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_ocspverify/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certs_ocspverify" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_ocspverify/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certs_ocspverify" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_ocspverify/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certs_ocspverify?label=swarmauri_certs_ocspverify&color=green" alt="PyPI - swarmauri_certs_ocspverify"/></a>

</p>

---

# swarmauri_certs_ocspverify

OCSP-based certificate verification service for the Swarmauri SDK.

This package provides an implementation of an `ICertService` that checks
certificate revocation status using the Online Certificate Status Protocol
(OCSP) defined in [RFC 6960](https://www.rfc-editor.org/rfc/rfc6960) while
remaining compatible with X.509 certificate guidelines from
[RFC 5280](https://www.rfc-editor.org/rfc/rfc5280).

## Features
- Parse PEM certificates to extract subject, issuer and OCSP responder URLs.
- Verify certificate status via OCSP responders advertised in the certificate's
  Authority Information Access extension.

## Installation
```bash
pip install swarmauri_certs_ocspverify
```

## Usage
```python
from swarmauri_certs_ocspverify import OcspVerifyService

svc = OcspVerifyService()
# verify and parse certificates using svc.verify_cert(...) and svc.parse_cert(...)
```
