![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_certs_csronly/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certs_csronly" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_csronly/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_csronly.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_csronly/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certs_csronly" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_csronly/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certs_csronly" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_csronly/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certs_csronly?label=swarmauri_certs_csronly&color=green" alt="PyPI - swarmauri_certs_csronly"/></a>

</p>

---

# swarmauri_certs_csronly

A community-provided certificate service that builds PKCS#10 Certificate Signing Requests (CSRs).

## Features
- Generate CSRs using RSA, EC, and Ed25519 keys
- Support for subject alternative names and basic constraints

## Installation
```bash
pip install swarmauri_certs_csronly
```

## Usage
```python
from swarmauri_certs_csronly import CsrOnlyService

service = CsrOnlyService()
csr_bytes = await service.create_csr(key_ref, {"CN": "example"})
```
