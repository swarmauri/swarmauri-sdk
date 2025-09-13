<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

<p align="center">
    <a href="https://pypi.org/project/swarmauri_certservice_scep/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certservice_scep" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_scep/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_scep.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_scep/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certservice_scep" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_scep/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certservice_scep" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_scep/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certservice_scep?label=swarmauri_certservice_scep&color=green" alt="PyPI - swarmauri_certservice_scep"/></a>
</p>

---

# Swarmauri Certservice SCEP

`ScepCertService` implements certificate enrollment using the [Simple Certificate Enrollment Protocol (SCEP)](https://datatracker.ietf.org/doc/html/rfc8894). It maps the generic `ICertService` flows onto SCEP operations so applications can request, receive, and validate X.509 certificates without dealing with protocol details.

## Features

- Build PKCS#10 certificate signing requests.
- Submit CSRs via SCEP `PKCSReq` and obtain signed certificates.
- Retrieve CA certificates and validate issued certificates.
- Parse X.509 certificates into convenient Python dictionaries.

## Installation

```bash
pip install swarmauri_certservice_scep
```

## Usage

```python
import asyncio
from swarmauri_certservice_scep import ScepCertService

async def main():
    service = ScepCertService("https://scep.example.test", challenge_password="secret")
    csr = await service.create_csr(key, {"CN": "device1"})
    cert = await service.sign_cert(csr, key)
    info = await service.verify_cert(cert)
    print(info)

asyncio.run(main())
```

Replace `key` with a `KeyRef` containing the private key material expected by the server.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
