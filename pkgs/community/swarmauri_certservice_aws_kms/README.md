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
