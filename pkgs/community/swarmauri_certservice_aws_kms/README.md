![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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
