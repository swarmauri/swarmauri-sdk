<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

<p align="center">
    <a href="https://pypi.org/project/swarmauri_certs_azure/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certs_azure" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_azure/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_azure.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_azure/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certs_azure" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_azure/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certs_azure" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_azure/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certs_azure?label=swarmauri_certs_azure&color=green" alt="PyPI - swarmauri_certs_azure"/></a>

</p>

---

# swarmauri_certs_azure

Community-maintained utilities for working with X.509 certificates via Azure Key Vault.

## Features
- AzureKeyVaultCertService for issuing and managing certificates.
- Helper utilities aligned with RFC 5280 and RFC 7468.

## Testing
Run tests with:
```bash
uv run --package swarmauri_certs_azure --directory community pytest
```
