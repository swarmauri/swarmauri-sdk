# swarmauri_cert_composite

Composite certificate service for Swarmauri.

This package provides `CompositeCertService`, a routing facade over multiple
`ICertService` providers.  It selects a provider based on advertised features or
an explicit `backend` option, allowing applications to work against a single
interface while leveraging different certificate backends (ACME, PKCS#11,
Vault, etc.).

## Features
- Delegated CSR creation (RFC 2986)
- Delegated certificate operations (RFC 5280)
- Optional backend override per call

## Optional Extras
- `aws`: support for AWS-based certificate providers.
- `vault`: support for Hashicorp Vault-based providers.

## Development
Run formatting and tests from the repository root:

```bash
uv run --directory pkgs/community/swarmauri_cert_composite --package swarmauri_cert_composite ruff format .
uv run --directory pkgs/community/swarmauri_cert_composite --package swarmauri_cert_composite ruff check . --fix
cd pkgs && uv run --package swarmauri_cert_composite --directory community/swarmauri_cert_composite pytest
```
