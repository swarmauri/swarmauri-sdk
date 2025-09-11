![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_certservice_ms_adcs/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certservice_ms_adcs" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_ms_adcs/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_ms_adcs.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_ms_adcs/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certservice_ms_adcs" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_ms_adcs/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certservice_ms_adcs" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_ms_adcs/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certservice_ms_adcs?label=swarmauri_certservice_ms_adcs&color=green" alt="PyPI - swarmauri_certservice_ms_adcs"/></a>

</p>

---

# swarmauri_certservice_ms_adcs

Community plugin providing a certificate service client for Microsoft Active Directory Certificate Services (AD CS).

## Features

- Build and sign PKCS#10 certificate signing requests (CSR) according to RFC 2986.
- Parse and verify X.509 certificates as defined in RFC 5280.
- Optional authentication helpers for NTLM and Kerberos.

## Installation

```bash
pip install swarmauri_certservice_ms_adcs[ntlm,kerberos]
```

## Usage

```python
from swarmauri_certservice_ms_adcs import MsAdcsCertService, _AuthCfg

svc = MsAdcsCertService(base_url="https://adcs.example.com/certsrv",
                        auth=_AuthCfg(mode="none"))
```
