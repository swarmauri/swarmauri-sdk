![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_certs_pkcs11/">
        <img src="https://static.pepy.tech/badge/swarmauri_certs_pkcs11/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_certs_pkcs11/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_certs_pkcs11.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_pkcs11/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_pkcs11/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certs_pkcs11" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_pkcs11/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certs_pkcs11?label=swarmauri_certs_pkcs11&color=green" alt="PyPI - swarmauri_certs_pkcs11"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Certs PKCS#11

A PKCS#11-backed certificate service implementing `CertServiceBase`.
It generates and verifies X.509 certificates using hardware security modules.

## Installation

```bash
pip install swarmauri_certs_pkcs11
```

## Entry Point

The service registers under the `swarmauri.cert_services` entry point as `Pkcs11CertService`.


