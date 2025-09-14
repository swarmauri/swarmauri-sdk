![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_certs_pkcs11/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certs_pkcs11" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_certs_pkcs11/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_certs_pkcs11.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_pkcs11/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certs_pkcs11" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_pkcs11/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certs_pkcs11" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_pkcs11/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certs_pkcs11?label=swarmauri_certs_pkcs11&color=green" alt="PyPI - swarmauri_certs_pkcs11"/></a>
</p>

---

# Swarmauri Certs PKCS#11

A PKCS#11-backed certificate service implementing `CertServiceBase`.
It generates and verifies X.509 certificates using hardware security modules.

## Installation

```bash
pip install swarmauri_certs_pkcs11
```

## Entry Point

The service registers under the `swarmauri.cert_services` entry point as `Pkcs11CertService`.
