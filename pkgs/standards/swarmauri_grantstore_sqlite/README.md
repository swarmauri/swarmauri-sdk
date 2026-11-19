![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# swarmauri_grantstore_sqlite

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_grantstore_sqlite)](https://pepy.tech/project/swarmauri_grantstore_sqlite)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_grantstore_sqlite.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_grantstore_sqlite)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_grantstore_sqlite)](https://pypi.org/project/swarmauri_grantstore_sqlite)
[![License](https://img.shields.io/pypi/l/swarmauri_grantstore_sqlite)](LICENSE)
[![Version](https://img.shields.io/pypi/v/swarmauri_grantstore_sqlite?label=swarmauri_grantstore_sqlite&color=green)](https://pypi.org/project/swarmauri_grantstore_sqlite)

Interchangeable grant stores component for the composable execution framework.

## Features

- Export `SqliteGrantStore` with SDK interface/base-class inheritance and entry-point discovery.
- Keep user authority, workload identity, lifecycle and delivery dependencies explicit.
- Reuse existing service registries, transports, checkpoints and token providers.
- Support Python 3.10, 3.11, 3.12, 3.13 and 3.14.

## Installation

Install the package with its declared dependencies. The composable APIs require swarmauri_core 0.11.0.dev8 or newer and swarmauri_base 0.11.0.dev13 or newer within the declared version bounds.

```sh
uv pip install ./pkgs/standards/swarmauri_grantstore_sqlite
pip install ./pkgs/standards/swarmauri_grantstore_sqlite
```

## Usage

The following is composition code. Injected dependency names are host configuration, not bundled mock providers. Async statements run inside an async function.

```python
from swarmauri_grantstore_sqlite import SqliteGrantStore

store = SqliteGrantStore(path="grants.db")
# Grant records are produced by the delegation service.
store.create(grant)
restored = store.load(grant.grant_id)
# save() returns an incremented revision and rejects stale writers.
```

See [the complete architecture and deployment guide](../../../docs/examples/composable-execution/README.md) for concrete local commands, live OIDC integration, HTTP hosting, lifecycle semantics and failure recovery.

## Verification

From `pkgs/`, with the workspace dependencies installed:

```sh
uv run --package swarmauri_grantstore_sqlite --directory standards/swarmauri_grantstore_sqlite pytest
uv run --package swarmauri_grantstore_sqlite --directory standards/swarmauri_grantstore_sqlite ruff check .
```

Tests use real signing and stores where applicable; scripted models are explicitly identified fixtures. No live provider interoperability is claimed by offline tests.

## Contributing

Follow the repository [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/AGENTS.md).
