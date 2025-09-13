<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

<p align="center">
    <a href="https://pypi.org/project/swarmauri_certservice_aws_kms/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certservice_aws_kms" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_aws_kms/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certservice_aws_kms.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_aws_kms/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certservice_aws_kms" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_aws_kms/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certservice_aws_kms" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certservice_aws_kms/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certservice_aws_kms?label=swarmauri_certservice_aws_kms&color=green" alt="PyPI - swarmauri_certservice_aws_kms"/></a>

</p>

---

# swarmauri_certservice_aws_kms

AWS KMS backed certificate service for Swarmauri.

This package provides an implementation of `CertServiceBase` that signs and verifies X.509 certificates using AWS Key Management Service.

## Features

- Create CSRs from exportable key material.
- Issue certificates using AWS KMS `Sign` API.
- Create self‑signed certificates.
- Verify and parse certificates with RFC 5280 compliance.

## Extras

- `docs`: documentation helpers.
- `perf`: benchmarking support.

## Testing

Run unit, functional and performance tests in isolation from the repository root:

```bash
uv run --package swarmauri_certservice_aws_kms --directory community/swarmauri_certservice_aws_kms pytest
```
