![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_certs_self_signed/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certs_self_signed" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_certs_self_signed/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_certs_self_signed.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_self_signed/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certs_self_signed" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_self_signed/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certs_self_signed" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_self_signed/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certs_self_signed?label=swarmauri_certs_self_signed&color=green" alt="PyPI - swarmauri_certs_self_signed"/></a>
</p>

---

# Swarmauri Self-Signed Certificate Builder

Standalone plugin providing utilities to issue self-signed X.509 certificates using the `SelfSignedCertificate` builder.

## Installation

```bash
pip install swarmauri_certs_self_signed
```

## Entry Point

This package registers `SelfSignedCertificate` under the `swarmauri.cert_services` entry point.
